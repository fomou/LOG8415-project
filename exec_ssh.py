from ipaddress import ip_address

import boto3
from botocore.exceptions import ClientError
import paramiko
import os


def get_LB_dns(ec2_client):
    filters = [
        {
            'Name': 'tag:Name',
            'Values': ['Proxy',"Trusted_Hosts","Manager"]
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


def execute_commands_on_ec2_instance(ec2_client):

    ip_address = get_LB_dns(ec2_client)
    print(f'Load Balancer ip adrress: {ip_address}')
    ssh_key = paramiko.RSAKey.from_private_key_file('test-key-pair.pem')
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=ip_address, username='ubuntu', pkey=ssh_key)
    stdin, stdout, stderr = ssh_client.exec_command('echo Hello from $(hostname)')
    print(stdout.read().decode())

    stdin, stdout, stderr = ssh_client.exec_command('cd /home/ubuntu/LOG8415-project && source /virt_en/bin/activate && pip3 install uvicorn && uvicorn main:app --host 0.0.0.0 --port 8080 &')
    print(stdout.read().decode())
    print(stderr.read().decode())

    ssh_client.close()

if __name__=='__main__':
    ec2_client = boto3.client('ec2')
    execute_commands_on_ec2_instance(ec2_client)
