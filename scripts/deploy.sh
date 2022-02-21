sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap
sudo npm install -g aws-cdk@1.x
cd ~/amazon-redshift-infrastructure-automation
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
#LINE='~/amazon-redshift-infrastructure-automation/scripts/restart_session.sh'
#FILE=~/.bashrc
#grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
aws configure set default.region us-east-1
read -n 1 -r -s -p $'[Input Required] Upload user-config.json and press enter to continue...\n'
read -p $'[Input Required] Enter a stack name: ' stack
read -p $'[Input Required] Enter your region: (e.g. us-east-1): ' current_region
export STACK_NAME=$stack
#Need more elegant solution for handling exception here:
[ -f ~/user-config.json ] && mv ~/user-config.json ~/amazon-redshift-infrastructure-automation/user-config.json
export account_id=`aws sts get-caller-identity --query "Account" --output text`
cdk bootstrap aws://$account_id/$current_region
cdk deploy --all --require-approval never
