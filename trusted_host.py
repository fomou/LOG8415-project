from flask import Flask, jsonify, request
import boto3
import requests
import random
app = Flask("__main__")
def names_private_ip():
    client = boto3.client('ec2', region_name='us-east-1')
    filters = [{'Name': 'tag:Name','Values': ['Proxy',"Gatekeeper"]}]
    response = client.describe_instances(Filters = filters)
    # Describe instances that match the filters
    names_ip ={}
    # Access the instance details
    if not response['Reservations']:
        print('No instances with the specified tag were found.')
    else:
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    name = instance['Tags'][0]['Value']
                    names_ip[name] = instance['PrivateIpAddress'] if name == 'Proxy' else instance['PublicIpAddress']

    return names_ip

@app.route("/ping")
def ping():
    return jsonify({"status":"healthy"})
@app.route("/table_size")
def get_table_size():
    ip = ip_table["Proxy"]
    response = requests.get(f'http://{ip}:5000/table_size')
    data = response.json()
    return jsonify(data)

@app.route("/read")
def read():
    response,_ = process_req("read")
    return jsonify(response)
@app.route("/write")
def write():
    response,_ = process_req("write")
    return jsonify(response)
def process_req(route):
    # Reject request from others hosts other than the gatekeeper
    # incoming_ip = request.remote_addr
    # if incoming_ip != ip_table["Gatekeeper"]:
    #     return {"status":f"Unauthorized IP {incoming_ip}", "code":401}
    # Assess the implementation type
    req_type = request.args.get("req_type")
    if req_type and req_type not in ["random","direct",'customize']:
        return {"status":f"Unauthorized implementation type {req_type}", "code":402}
    # Forward the request to the proxy on its private IP as it's reachable over internet
    private = ip_table["Proxy"]
    response = requests.get(f'http://{private}:5000/{route}?req_type={req_type}')
    return jsonify(response.json())


if __name__ == "__main__":
    ip_table = names_private_ip()
    app.run(host='0.0.0.0', port=5050)