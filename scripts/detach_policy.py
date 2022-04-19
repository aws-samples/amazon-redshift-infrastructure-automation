import boto3
import json
import os

stackname = os.getenv('STACK_NAME')

region_name = boto3.session.Session().region_name
session = boto3.session.Session()
sm_client = session.client(
                    service_name='iam',
                                    region_name=region_name,
                                                    )
iam = boto3.resource('iam')
response = sm_client.list_roles()

for role in response['Roles']:
            if 'WindowsCLIrole' in role['RoleName']:
              x = role['RoleName']
              print(x)
              response = sm_client.detach_role_policy(
                RoleName=x,
                PolicyArn='arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore'
            )
