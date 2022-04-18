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
if [ -z "${ONPREM_CIDR}" ]
then
        read -p $'[Input Required] Enter your on prem CIDR range (format xxx.xxx.xxx.xxx/xx): ' onprem_cidr
        export ONPREM_CIDR=$onprem_cidr
fi
cdk destroy --all --require-approval never
python3 ./scripts/delete_secrets.py
python3 ./scripts/delete_buckets.py
