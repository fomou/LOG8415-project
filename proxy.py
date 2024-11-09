
from flask import Flask, jsonify, request
import boto3
import requests
import random
app = Flask("__main__")
def names_private_ip():
    client = boto3.client('ec2', region_name='us-east-1')
    filters = [
        {
            'Name': 'tag:Name',  # Filtering by the 'Environment' tag
            'Values': ['Manager',"worker1", "worker2"]
        }
    ]
    response = client.describe_instances(Filters = filters)
    print("")
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
                    names_ip[name] = instance['PrivateIpAddress']

    return names_ip
@app.route("/ping")
def ping():
    return jsonify({"status": "healthy"}),200
@app.route("/read")
def read():
        req_type = request.args.get("req_type")
        outcome =process_request("read",req_type)
        return outcome
@app.route("/write")
def write():
    req_type = request.args.get("req_type")
    outcome = process_request("write", req_type)
    return outcome
@app.route("/table_size")
def get_table_size():
    data = {}
    for name in ["Manager","worker1","worker2"]:
        ip = name_ip[name]
        response = requests.get(f'http://{ip}:5000/table_size')
        if response.status_code == 200:
            data[name] = response.json()
    return jsonify(data)

def process_request(route,req_type):
    if req_type == "Direct" or not req_type:
        ip = name_ip["Manager"]
        response = requests.get(f'http://{ip}:5000/{route}')

        if response.status_code == 200:
            return jsonify({"Type": req_type, "Processed by": "Manager", "value": response.json()})
    elif req_type == "random":
        name = random.choice(["Manager", "worker1", "worker2"])
        ip = name_ip[name]
        response = requests.get(f'http://{ip}:5000/{route}')
        if response.status_code == 200:
            return jsonify({"Type": req_type, "Processed by": name, "value": response.json()})
    elif req_type == "customize":
        responses_time = {}

        for name, ip in name_ip.items():
            response = requests.get(f'http://{ip}:5000/ping')
            if response.status_code == 200:
                responses_time[name] = response.elapsed

        best_name = min(responses_time, key=responses_time.get)
        ip = name_ip[best_name]
        response = requests.get(f'http://{ip}:5000/{route}')

        if response.status_code == 200:
            return jsonify({"Type": req_type, "Processed by": best_name, "value": response.json()})

if __name__ == "__main__":
    name_ip = names_private_ip()
    app.run(host='0.0.0.0', port=5000)
