# Runs and deploys CDK
sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap
sudo npm install -g aws-cdk
cd ~/amazon-redshift-infrastructure-automation
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
if [ -z "${STACK_NAME}" ]
then
        read -p $'[Input Required] Enter a stack name: ' stack
        export STACK_NAME=$stack
fi
#if [ -z "${ONPREM_CIDR}" ]
#then
#        read -p $'[Input Required] Enter your on prem CIDR range (format xxx.xxx.xxx.xxx/xx): ' onprem_cidr
#        export ONPREM_CIDR=$onprem_cidr
#fi
export ONPREM_CIDR=12.34.56.78/32
python3 ./scripts/delete_buckets.py
python3 ./scripts/detach_policy.py
cdk destroy --all --require-approval never
aws cloudformation delete-stack --stack-name CDKToolkit

python3 << EOF
import boto3
import json
import os
import delete_secrets
stackname = os.getenv('STACK_NAME')
region_name = boto3.session.Session().region_name
session = boto3.session.Session()
sm_client = session.client(
    service_name='secretsmanager',
    region_name=region_name,
)
secrets_list = [f"{stackname}-SourceDBPassword",
                f"{stackname}-RedshiftPassword",
                f"{stackname}-RedshiftClusterSecretAA"]

sm_response = sm_client.list_secrets()
for secret in sm_response['SecretList']:
    if secret['Name'] in secrets_list:
      execfile('delete_secrets.py')
EOF
