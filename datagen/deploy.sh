echo "Installing dependencies...."; sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap > /dev/null; echo " done."
echo "Installing aws-cdk...."; sudo npm install -g aws-cdk > /dev/null; echo " done."

chmod +x ~/datagencdk/menu-welcome-message.sh
chmod +x ~/datagencdk/menu-script.sh

cd ~/datagencdk/
python3 -m venv .env
source .env/bin/activate
echo "Installing requirements...."; pip install -r requirements.txt > /dev/null; echo " done."

aws configure set default.region us-east-1

~/datagencdk/menu-welcome-message.sh
~/datagencdk/menu-script.sh

cdk deploy --all --require-approval never
