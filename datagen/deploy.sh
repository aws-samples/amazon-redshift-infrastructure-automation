echo "Installing dependencies...."; sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap > /dev/null; echo " done."
echo "Installing aws-cdk...."; sudo npm install -g aws-cdk > /dev/null; echo " done."

chmod +x ~/amazon-redshift-infrastructure-automation/datagen/menu-welcome-message.sh
chmod +x ~/amazon-redshift-infrastructure-automation/datagen/menu-script.sh

cd ~/amazon-redshift-infrastructure-automation/datagen/
python3 -m venv .env
source .env/bin/activate
echo "Installing aws-cdk.aws-lambda-python-alpha...."; pip install aws-cdk.aws-lambda-python-alpha > /dev/null; echo " done."
echo "Installing requirements...."; pip install -r requirements.txt > /dev/null; echo " done."

aws configure set default.region us-east-1

~/amazon-redshift-infrastructure-automation/datagen/menu-welcome-message.sh
~/amazon-redshift-infrastructure-automation/datagen/menu-script.sh

cdk deploy --all --require-approval never
