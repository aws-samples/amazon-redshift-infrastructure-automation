sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap
sudo npm install -g aws-cdk
cd ~/amazon-redshift-infrastructure-automation
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
LINE='~/amazon-redshift-infrastructure-automation/scripts/restart_session.sh'
FILE='~/.bashrc'
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
read -n 1 -r -s -p $'[Input Required] Upload user-config.json and press enter to continue...\n'
#Need more elegant solution for handling exception here:
[ -f ~/user-config.json ] && mv ~/user-config.json ~/amazon-redshift-infrastructure-automation/user-config.json
cdk deploy --all --require-approval never