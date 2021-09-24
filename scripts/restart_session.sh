# Reinstall required yum packages
sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap
# Reinstall CDK
sudo npm install -g aws-cdk
# Activates Python virtual environment
source ~/amazon-redshift-infrastructure-automation/.env/bin/activate
# Reinstall required python libraries
pip install -r ~/amazon-redshift-infrastructure-automation/requirements.txt
# clear screen
clear