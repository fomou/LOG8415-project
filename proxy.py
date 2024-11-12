
from flask import Flask, jsonify, request
import boto3
import requests
import random
app = Flask("__main__")

@app.route("/ping")
def ping():
    return jsonify({"status": "healthy"}),200

@app.route("/read")
def read():
        req_type = request.args.get("req_type")
        outcome =process_request("read",req_type)
        return jsonify(outcome)

@app.route("/write")
def write():
    ip = name_ip["Manager"]
    response = requests.get(f'http://{ip}:5000/write')
    return jsonify(response)
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
    name_ip = {'Manager': '172.198.100.3','work1':"172.198.100.4", "worker2":'172.198.100.5'}
    app.run(host='0.0.0.0', port=5000)
