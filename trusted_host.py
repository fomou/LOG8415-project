from flask import Flask, jsonify, request
import boto3
import requests
import random
app = Flask("__main__")


@app.route("/ping")
def ping():
    return jsonify({"status":"healthy"})

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
    # Assess the implementation type
    req_type = request.args.get("req_type")
    if req_type and req_type not in ["random","direct",'customize']:
        return "Unauthorized", 401
    # Forward the request to the proxy on its private IP as it's reachable over internet
    private = ip_table["Proxy"]
    response = requests.get(f'http://{private}:5000/{route}?req_type={req_type}')
    return jsonify(response.json()),response.status_code


if __name__ == "__main__":
    ip_table = {'Proxy':'172.31.16.2' ,"Gatekeeper":'172.31.16.6'}
    app.run(host='0.0.0.0', port=5050)