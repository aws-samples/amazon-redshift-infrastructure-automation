# Install the required software
sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap
sudo npm install -g aws-cdk
cd ~/amazon-redshift-infrastructure-automation
# Creates a python virtual environment that will be used by CDK
python3 -m venv .env
source .env/bin/activate
# Installs the required python libraries in the virtual environment
pip install -r requirements.txt
# adds the restart_session script that reinstall CDK in CloudShell if in case connection is restarted.
LINE='~/amazon-redshift-infrastructure-automation/scripts/restart_session.sh'
FILE=~/.bashrc
grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
# Waits for user input to ensure that user-config.json is uploaded
read -n 1 -r -s -p $'[Input Required] Upload user-config.json and press enter to continue...\n'
# Moves the user-config.json to the project folder
[ -f ~/user-config.json ] && mv ~/user-config.json ~/amazon-redshift-infrastructure-automation/user-config.json
# Runs and deploys CDK
cdk deploy --all --require-approval never