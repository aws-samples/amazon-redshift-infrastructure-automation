import boto3
import json

region_name = boto3.session.Session().region_name
session = boto3.session.Session()
sm_client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
)

config = json.load(open("../user-config.json"))
secrets_list = [f"{config['stack_name']}-SourceDBPassword",
                f"{config['stack_name']}-RedshiftPassword",
                f"{config['stack_name']}-RedshiftClusterSecretAA"]

sm_response = sm_client.list_secrets()
for secret in sm_response['SecretList']:
    if secret['Name'] in secrets_list:
        response = sm_client.delete_secret(
            SecretId=secret['Name']
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f"{secret['Name']} successfully deleted")
        else:
            print(f"Error: {response}")
