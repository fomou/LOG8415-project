from flask import Flask, jsonify, request
import boto3
import requests
import random
app = Flask("__main__")
def trusted_host_ip():
    client = boto3.client('ec2', region_name='us-east-1')
    filters = [{'Name': 'tag:Name','Values': ['Trusted_Hosts']}]
    response = client.describe_instances(Filters = filters)
    # Describe instances that match the filters
    # Access the instance details
    if not response['Reservations']:
        print('No instances with the specified tag were found.')
    else:
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    return instance['PublicIpAddress']
@app.route("/ping")
def ping():
    return jsonify({"status": "healthy"}),200
@app.route("/read")
def read():
    req_type = request.args.get("req_type")
    private = trusted_host_ip()
    response = requests.get(f'http://{private}:5050/read?req_type={req_type}')
    return response.json(), response.status_code

@app.route("/write")
def write():
    req_type = request.args.get("req_type")
    private = trusted_host_ip()
    response = requests.get(f'http://{private}:5050/write')
    return response.json(), response.status_code
@app.route("/table_size")
def get_table_size():
    ip = trusted_host_ip()
    response = requests.get(f'http://{ip}:5050/table_size')
    data = response.json()
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)