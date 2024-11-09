from doctest import master

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
class Infrastructure:
    def __init__(self):
        self.sec_group_id_1 = ''
        self.key_pair_name= "Project-key-pair"
        self.VPC_id = ""
        self.cidr = ""
        self.sec_group_id_2 = ""

    def verify_valid_credentials(self):
        try:
            sts_client = boto3.client('sts')
            sts_client.get_caller_identity()
            print("Valid credentials")
        except NoCredentialsError as e:
            print("No credentials found")
        except ClientError as e:
            print(f"Error: {e}")

    def create_security_group(self,client, name):
        response_vpcs = client.describe_vpcs()
        self.VPC_id = response_vpcs.get('Vpcs', [{}])[0].get('VpcId', '')
        self.cidr =  response_vpcs['Vpcs'][0]['CidrBlock']
        response_security_group = client.create_security_group(
            GroupName="Internet",
            Description='Security allowing all traffic',
            VpcId=self.VPC_id)

        self.sec_group_id_1 = response_security_group['GroupId']

        response_security_group_2 = client.create_security_group(
            GroupName="Internal",
            Description='Security group for internal only',
            VpcId=self.VPC_id)
        self.sec_group_id_2 = response_security_group_2["GroupId"]
        self.sec_group_id_1 = response_security_group['GroupId']

        client.authorize_security_group_ingress(
            GroupId=self.sec_group_id_1,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                 'FromPort': 80,
                 'ToPort': 80,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': '-1',
                 'FromPort': 0,
                 'ToPort': 65535,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                 'FromPort': 22,
                 'ToPort': 22,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            ])

        client.authorize_security_group_ingress(
            GroupId=self.sec_group_id_2,
            IpPermissions=[
                {'IpProtocol': '-1',
                 'FromPort': 0,
                 'ToPort': 65535,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])

    def create_login_key_pair(self,ec2_client):
        key_pair = ec2_client.create_key_pair(KeyName=self.key_pair_name, KeyType='rsa')
        print("Creating a key-pair to connect to the instances")
        with open(f'{self.key_pair_name}.pem', 'w') as file:
            file.write(key_pair.key_material)
        os.chmod(f'{self.key_pair_name}.pem', 0o444)

    def create_micro_instances(self,ec2_client,secGroupId, user_data, name):
        try:
            response = ec2_client.create_instances(ImageId='ami-0e86e20dae9224db8',
                                                   MaxCount=1, InstanceType='t2.micro',
                                                   MinCount=1, KeyName=self.key_pair_name,
                                                   TagSpecifications=[{'ResourceType': 'instance',
                                                                       'Tags': [{'Key': 'Name',
                                                           'Value': name}]}],
                                                   SecurityGroupIds=[secGroupId],
                                                   UserData=user_data)
            print(f"Creating {name}")
            return response[0]
        except ClientError as e:
            print(f"Error: {e}")

    def create_large_instances(self,ec2_client,secGroupId, user_data, name):
        try:
            response = ec2_client.create_instances(ImageId='ami-0e86e20dae9224db8',
                                                   MaxCount=1, InstanceType='t2.large',
                                                   MinCount=1, KeyName=self.key_pair_name,
                                                   TagSpecifications=[{'ResourceType': 'instance',
                                                                       'Tags': [{'Key': 'Name',
                                                           'Value': name}]}],
                                                   SecurityGroupIds=[secGroupId],
                                                   UserData=user_data)
            print(f"Creating {name}")
            return response[0]
        except ClientError as e:
            print(f"Error: {e}")
if __name__ == '__main__':
    client = boto3.client('ec2')
    ec2_res = boto3.resource('ec2')

    infra = Infrastructure()
    user_data = open('user_data_mysql.sh').read()
    infra.verify_valid_credentials()
    infra.create_security_group(client,"sec-group-project")
    infra.create_login_key_pair(ec2_res)
    # Creating 3 micro the MySql cluster
    names = ['Manager', 'worker1','worker2']
    for name in names :
        infra.create_micro_instances(ec2_res, infra.sec_group_id_2,user_data, name)


    proxy_user_data = open('user_data_proxy.sh').read()

    infra.create_large_instances(ec2_res,infra.sec_group_id_1, user_data,"Proxy")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
