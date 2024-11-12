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
    private = '172.198.100.1'
    response = requests.get(f'http://{private}:5050/read?req_type={req_type}')
    return jsonify(response.json()), response.status_code

@app.route("/write")
def write():
    req_type = request.args.get("req_type")
    private  = '172.198.100.1'
    response = requests.get(f'http://{private}:5050/write')
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)