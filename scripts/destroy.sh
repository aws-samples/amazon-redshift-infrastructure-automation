# Runs and deploys CDK
cd ~/amazon-redshift-infrastructure-automation
cdk destroy --all --require-approval never
source .env/bin/activate
python3 delete_secrets.py