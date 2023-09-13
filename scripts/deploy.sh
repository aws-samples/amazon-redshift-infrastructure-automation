echo "Installing dependencies...."; sudo yum -y install gcc gcc-c++ python3 python3-devel unixODBC unixODBC-devel aws-cfn-bootstrap > /dev/null; echo " done."
echo "Installing aws-cdk...."; sudo npm install -g aws-cdk@2.x > /dev/null; echo " done."
chmod +x ~/amazon-redshift-infrastructure-automation/scripts/shell_menu/menu-script.sh
chmod +x ~/amazon-redshift-infrastructure-automation/scripts/shell_menu/bash-menu-cli-commands.sh
chmod +x ~/amazon-redshift-infrastructure-automation/scripts/shell_menu/menu-welcome-message.sh
chmod +x ~/amazon-redshift-infrastructure-automation/scripts/shell_menu/miscdetails.sh

cd ~/amazon-redshift-infrastructure-automation
python3 -m venv .env
source .env/bin/activate
echo "Installing requirements...."; pip install -r requirements.txt > /dev/null; echo " done."
#LINE='~/amazon-redshift-infrastructure-automation/scripts/restart_session.sh'
#FILE=~/.bashrc
#grep -qF -- "$LINE" "$FILE" || echo "$LINE" >> "$FILE"
aws configure set default.region us-east-1
~/amazon-redshift-infrastructure-automation/scripts/shell_menu/menu-welcome-message.sh
 read -r -p "Do you have an existing user-config.json file? (Yy/Nn): " answer
    case $answer in
        [Yy]* ) read -r -p "Please upload your user-config.json file and press ENTER to continue..." answer;
                 source ~/amazon-redshift-infrastructure-automation/scripts/shell_menu/miscdetails.sh;;
        [Nn]* ) source ~/amazon-redshift-infrastructure-automation/scripts/shell_menu/menu-script.sh;;
        * ) echo "Please answer Y or N.";;
    esac
export STACK_NAME=$stack
export ONPREM_CIDR=$onprem_cidr
export JSII_SILENCE_WARNING_DEPRECATED_NODE_VERSION=true
#Need more elegant solution for handling exception here:
[ -f ~/user-config.json ] && mv ~/user-config.json ~/amazon-redshift-infrastructure-automation/user-config.json
export account_id=`aws sts get-caller-identity --query "Account" --output text`
if [ "$loadTPCdata" = "Y" ];
then
cdk bootstrap aws://$account_id/$current_region
fi
cdk deploy --all --require-approval never
