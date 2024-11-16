import asyncio
import json
import aiohttp
import time
from time import sleep
import boto3
from botocore.exceptions import ClientError
from pprint import pprint

def get_gatekeeper_ip(ec2_client):
    filters = [
        {
            'Name': 'tag:Name',
            'Values': ['Gatekeeper']
        }
    ]

    response = ec2_client.describe_instances(Filters=filters)

    if not response['Reservations']:
        print('No instances with the specified tag were found.')
    else:
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                        return instance['PublicIpAddress']

async def call_endpoint_http (load_balancer_url, session , request_num, data ) :
    url = load_balancer_url
    headers = {'content-type': 'application/json'}

    try:
        async with session.get(url, headers=headers) as response :
            status_code = response.status
            response_json = await response.json()
            print ( f" Request { request_num }: Status Code : { status_code}")
            data[request_num] = response_json
            return status_code , response_json
    except Exception as e :
        print ( f" Request { request_num }: Failed - {str(e)}")
        return None , str(e)

async def main() :
    num_requests = 1000
    start_time = time.time()

    elb_client = boto3.client('elbv2')
    c2_client = boto3.client('ec2')


    try:
        gatekeeper_ip = get_gatekeeper_ip(c2_client)
        print(f"tables size before write operations")
        async with aiohttp.ClientSession() as session:
            await print_tables_size(f'http://{gatekeeper_ip}:5000/table_size', session)
        print('\n************* sending writing request *************\n')
        start_time = time.time()
        data = {}
        # async with aiohttp.ClientSession() as session:
        #     write_url = f'http://{gatekeeper_ip}:5000/write'
        #     tasks = [call_endpoint_http(write_url, session, i, data) for i in range(num_requests)]
        #     await asyncio.gather(*tasks)

        end_time = time.time()
        print(f"\nTotal time taken : {end_time - start_time :.2f} seconds ")
        print(f"Average time per request : {(end_time - start_time) / num_requests :.4f} seconds ")
        print(f"*************tables size after write operations***********")
        async with aiohttp.ClientSession() as session:
            await print_tables_size(f'http://{gatekeeper_ip}:5000/table_size', session)
        implementations = ["random","direct","customize"]
        for imp in implementations:
            print(f"******************* sending {num_requests} read requests for implementation {imp}***************")
            read_url = f'http://{gatekeeper_ip}:5000/read?req_type={imp}'
            data ={}
            start_time = time.time()
            async with aiohttp.ClientSession() as session :
                tasks = [ call_endpoint_http (read_url, session , i,data) for i in range(num_requests )]
                await asyncio.gather(*tasks)
            with open(f'myfile_{imp}.json', 'w', encoding='utf8') as json_file:
                json.dump(data, json_file, allow_nan=True)
            end_time = time.time()
            print ( f"\nTotal time taken for {imp} implementation: { end_time - start_time :.2f} seconds ")
            print ( f"Average time per request : {(end_time - start_time)/num_requests:.4f} seconds ")

    except ClientError as e:
        print(e)
async def print_tables_size(url, session):
    try:
        headers = {'content-type': 'application/json'}
        async with session.get(url, headers=headers) as response:
            status_code = response.status
            response_json = await response.json()
            pprint(response_json)
    except Exception as e:
        print(f" Request : Failed - {str(e)}")
if __name__ == "__main__":
    asyncio.run(main())