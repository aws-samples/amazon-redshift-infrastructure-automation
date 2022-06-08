echo "Installing dependencies...."; sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap > /dev/null; echo " done."
echo "Installing aws-cdk...."; sudo npm install -g aws-cdk@1.x > /dev/null; echo " done."
chmod +x ~/amazon-redshift-infrastructure-automation/scripts/menu-script.sh
chmod +x ~/amazon-redshift-infrastructure-automation/scripts/bash-menu-cli-commands.sh
cd ~/amazon-redshift-infrastructure-automation
python3 -m venv .env
source .env/bin/activate
echo "Installing requirements...."; pip install -r requirements.txt > /dev/null; echo " done."
#LINE='~/amazon-redshift-infrastructure-automation/scripts/restart_session.sh'
#FILE=~/.bashrc
#grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
aws configure set default.region us-east-1
~/amazon-redshift-infrastructure-automation/scripts/menu-script.sh
read -p $'[Input Required] Enter a stack name: ' stack
read -p $'[Input Required] Enter your region: (e.g. us-east-1): ' current_region
read -p $'[Input Required] Enter your on prem CIDR range (format xxx.xxx.xxx.xxx/xx): ' onprem_cidr
export STACK_NAME=$stack
export ONPREM_CIDR=$onprem_cidr
#Need more elegant solution for handling exception here:
[ -f ~/user-config.json ] && mv ~/user-config.json ~/amazon-redshift-infrastructure-automation/user-config.json
export account_id=`aws sts get-caller-identity --query "Account" --output text`
cdk bootstrap aws://$account_id/$current_region
cdk deploy --all --require-approval never
