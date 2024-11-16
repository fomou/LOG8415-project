from flask import Flask, jsonify
from mysql.connector import connect
import boto3
import requests
import random

app = Flask(__name__)

def names_private_ip():
    client = boto3.client('ec2', region_name='us-east-1')
    filters = [
        {
            'Name': 'tag:Name',  # Filtering by the 'Environment' tag
            'Values': ["worker1", "worker2"]
        }
    ]
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
                    names_ip[name] = instance['PrivateIpAddress']

    return names_ip

def get_connector():

    connection = connect(
        host='localhost',        # MySQL server address (localhost or IP)
        user='root',             # MySQL username
        # MySQL password
        database='sakila' # Database name
    )
    return connection

@app.route("/ping")
def ping():
    return jsonify({"status": "healthy"}),200

@app.route("/read")
def read_data():
    connection = get_connector()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM test")
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify({"data":row}), 200

@app.route("/write")
def write():
    connection = get_connector()
    cursor = connection.cursor(dictionary=True)
    name_ = f'name_{random.randint(0, 1000)}'
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INT AUTO_INCREMENT,name VARCHAR(255),PRIMARY KEY (id));")
    cursor.execute(f"INSERT INTO test (name) VALUES ('{name_}');")

    row = cursor.fetchall()
    cursor.close()
    connection.commit()
    connection.close()
    for name in ["worker1","worker2"]:
        ip = name_ip[name]
        response = requests.get(f"http://{ip}:5000/write?name={name_}")
        print(response)
    return jsonify({'write':"finish"}), 200

@app.route("/table_size")
def get_table_size():
    connection = get_connector()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as size FROM test")
    row = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(row[0]), 200

if __name__ == "__main__":
    name_ip = names_private_ip()
    app.run(host='0.0.0.0', port=5000) # Adjust port if needed