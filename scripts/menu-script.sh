
#CREATE/NA
metReqs=""
vpc_id=""
redshift_endpoint=""
dms_migration_to_redshift_target=""
sct_on_prem_to_redshift_target=""
jmeter=""
#VPC DETAILS
cidr=""
number_of_az=""
cidr_mask=""
existing_vpc_id=""
#REDSHIFT DETAILS
existing_RS_id=""
cluster_identifier=""
database_name=""
node_type=""
number_of_nodes=""
master_user_name=""
subnet_type=""
encryption=""
loadTPCdata=""
#DMS Details
migration_type=""
dms_subnet_type=""
source_db=""
source_engine=""
source_schema=""
source_host=""
source_user=""
source_port="1"
#SCT KeyName
sct_key_name=""
#JMeter KeyName
key_name=""
jmeter_node_type="c5.9xlarge"
## Colored input's
RESET="\033[0m"
BOLD="\033[1m"
YELLOW="\033[38;5;11m"
BLUE="\033[36;5;11m"
coloredQuestion="$(echo -e [$BOLD$YELLOW"??"$RESET])"
coloredLoading="$(echo -e $BOLD$BLUE"..."$RESET)"
function box_out()
{
  local s=("$@") b w
  for l in "${s[@]}"; do
    ((w<${#l})) && { b="$l"; w="${#l}"; }
  done
  tput setaf 3
  echo " -${b//?/-}-
| ${b//?/ } |"
  for l in "${s[@]}"; do
    printf '| %s%*s%s |\n' "$(tput setaf 4)" "-$w" "$l" "$(tput setaf 3)"
  done
  echo "| ${b//?/ } |
 -${b//?/-}-"
  tput sgr 0
}

box_out "Welcome!" "This utility tool will help you create the required resources for $(whoami)" "Please review the pre-requisites at the following link before proceeding: " "" "https://github.com/aws-samples/amazon-redshift-infrastructure-automation#prerequisites"
echo
while true; do
    read -r -p "$coloredQuestion[Input Required] Are the prerequisites met?(Y/N):" answer
    case $answer in
        [Yy]* ) break;;
        [Nn]* ) 
            echo "Please visit the link below"
            echo "https://github.com/aws-samples/amazon-redshift-infrastructure-automation#prerequisites"; 
            metReqs="N"
            exit;;
        * ) echo "Please answer Y or N.";;
    esac
done
echo
#VPC
while true; do
    read -r -p "$coloredQuestion[Input Required] Do you wish to create a new VPC? (Y/N):" answer
    case $answer in
        [Yy]* ) export vpc_id="CREATE"; 
                 break;;
        [Nn]* ) export vpc_id="N/A"; break;;
        * ) echo "Please answer Y or N.";;
    esac
done
echo
if [ "$vpc_id" = "CREATE" ]; 
then 
    echo "Please configure VPC details..."
    read -r -p "$coloredQuestion [Input Required][VPC Details]: Please provide a VPC CIDR Range (format xxx.xxx.xxx.xxx/xx): " cidr
    read -r -p "$coloredQuestion [Input Required][VPC Details]: How many Availability Zones: " number_of_az
    read -r -p "$coloredQuestion [Input Required][VPC Details]: Please provide a CIDR MASK(number only, no /): " cidr_mask

elif [ "$vpc_id" = "N/A" ];
then
    
    echo "[$coloredLoading]Loading your VPC's..."
    ~/amazon-redshift-infrastructure-automation/scripts/bash-menu-cli-commands.sh
    readarray -t list < vpclist.txt
    PS3='[Input Required] Please select your VPC: '
    select selection in "${list[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        
            vpc_id=$selection
            break
        fi
    done
    echo "You have choosen $selection"
fi

#REDSHIFT 
while true; do
    read -r -p "$coloredQuestion[Input Required] Do you wish to create a new Redshift? (Y/N): " answer
    case $answer in
        [Yy]* ) export redshift_endpoint="CREATE"; break;;
        [Nn]* ) export redshift_endpoint="N/A"; break;;
        * ) echo "Please answer Y or N.";;
    esac
done

if [ "$redshift_endpoint" = "CREATE" ]; 
then 
    echo "[Input Required][REDSHIFT Details]: Please configure Redshift details..."
    read -r -p "$coloredQuestion[Input Required][REDSHIFT Details]: Please provide a cluster indentifier: " cluster_identifier
    read -r -p "$coloredQuestion[Input Required][REDSHIFT Details]: Please provide a Redshift database name: " database_name
    read -r -p "$coloredQuestion[Input Required][REDSHIFT Details]: Please provide a master user name: " master_user_name 

    PS3='[Input Required][REDSHIFT Details]: Please select your Redshift node type choice: '
    options=("ds2.xlarge" "ds2.8xlarge" "dc1.large" "dc1.8xlarge" "dc2.large" "dc2.8xlarge" "ra3.xlplus" "ra3.4xlarge" "ra3.16xlarge" )
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            node_type=$selection
            break
        fi   
    done

    read -r -p "$coloredQuestion[Input Required][REDSHIFT Details]: How many nodes of $node_type? " number_of_nodes
    
    PS3='[Input Required][REDSHIFT Details]: Please select subnet type: '
    options=("PUBLIC" "PRIVATE" "ISOLATED")
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            subnet_type=$selection
            break
        fi     
    done
    
    while true; do
    read -r -p "$coloredQuestion[Input Required][REDSHIFT Details]: Would you like to use encryption? (Y/N) " answer
    case $answer in
        [Yy]* ) export encryption="Y"; break;;
        [Nn]* ) export encryption="N"; break;;
        * ) echo "Please answer Y or N.";;
    esac
    done
    while true; do
    read -r -p "$coloredQuestion[Input Required][REDSHIFT Details]: Would you like to load TPC data? (Y/N) " loadTPCdata
    case $loadTPCdata in
        [Yy]* ) export loadTPCdata="Y"; break;;
        [Nn]* ) export loadTPCdata="N"; break;;
        * ) echo "Please answer Y or N.";;
    esac
    done        
   
    
elif [ "$redshift_endpoint" = "N/A" ];
then
    echo "[$coloredLoading]Loading your Redshift Clusters..."
     ~/amazon-redshift-infrastructure-automation/scripts/bash-menu-cli-commands.sh
            readarray -t list < redshiftlist.txt
            PS3='[Input Required] Please select your Redshift Cluster: '
            select selection in "${list[@]}"; do
                if [[ $REPLY == "0" ]]; then
                    echo 'Goodbye' >&2
                    exit
                else
                    redshift_endpoint=$selection
                    break
                fi
            done
            echo "You have choosen $selection"
fi

#####DMS
while true; do
    read -r -p "$coloredQuestion[Input Required] Do you have an external database that you would like to migrate using DMS? (Y/N): " answer
    case $answer in
        [Yy]* ) export dms_migration_to_redshift_target="CREATE"; break;;
        [Nn]* ) export dms_migration_to_redshift_target="N/A"; break;;
        * ) echo "Please answer Y or N.";;   
    esac
done

if [ "$dms_migration_to_redshift_target" = "CREATE" ]; 
then
    PS3='[Input Required][DMS Details]: Please select subnet type for DMS: '
    options=("PUBLIC" "PRIVATE" "ISOLATED" )
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            dms_subnet_type=$selection
            break
        fi     
    done
    PS3='[Input Required][DMS Details]: Please select your migration type: '
    options=( "full-load" "cdc" "full-load-and-cdc")
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            migration_type=$selection
            break
        fi   
    done
    PS3='[Input Required][DMS DETAILS] What is the engine type: '
    options=( "mysql" "oracle" "postgres" "mariadb" "aurora" "aurora-postgresql" "opensearch" "redshift" "s3" "db2" "azuredb" "sybase" "dynamodb" "mongodb" "kinesis" "kafka" "elasticsearch" "docdb" "sqlserver" "neptune")
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            source_engine=$selection
            break
        fi   
    done
    read -r -p "$coloredQuestion[Input Required][DMS DETAILS] Please provide name of source database to migrate: " source_db
    read -r -p "$coloredQuestion[Input Required][DMS DETAILS] What is the name of source schema: " source_schema
    read -r -p "$coloredQuestion[Input Required][DMS DETAILS] What is the name of source host: " source_host
    read -r -p "$coloredQuestion[Input Required][DMS DETAILS] What is the source user: " source_user
    read -r -p "$coloredQuestion[Input Required][DMS DETAILS] What is the source port: " source_port
fi

if [ "$dms_migration_to_redshift_target" = "CREATE" ]; 
then 
while true; do
    read -r -p "$coloredQuestion[Input Required] Do you need SCT? (Y/N)" answer
    case $answer in
        [Yy]* ) export sct_on_prem_to_redshift_target="CREATE"; break;;
        [Nn]* ) export sct_on_prem_to_redshift_target="N/A"; break;;
        * ) echo "Please answer Y or N.";;   
    esac
done
fi

if [ "$sct_on_prem_to_redshift_target" = "CREATE" ]; 
then
    echo "[$coloredLoading]Loading your account keypairs..."
    ~/amazon-redshift-infrastructure-automation/scripts/bash-menu-cli-commands.sh
     readarray -t list < keypairlist.txt
        number=$(wc -l < keypairlist.txt) 
        if [ $number = "0" ]; 
        then 
            read -p "$coloredQuestion[Input Required] Your selected region has no account keypairs. Please enter a name for one: " key_name
        else
            PS3='[Input Required] Please select the keypair for SCT: '
            select selection in "${list[@]}"; do
            key_name=$selection
            break
            done
        fi
        
        echo "You have choosen $selection"
fi

while true; do
    read -r -p "$coloredQuestion[Input Required] Would you like to use Jmeter? (Y/N): " answer
    case $answer in
        [Yy]* ) export jmeter="CREATE"; break;;
        [Nn]* ) export jmeter="N/A"; break;;
        * ) echo "Please answer Y or N.";;
    esac
done

if [ "$jmeter" = "CREATE" ]; 
then 
    PS3='[Input Required][REGION] Please select your ec2 nodetype for Jmeter: '
    options=("c5.9xlarge" "c5.12xlarge" "c5.18xlarge" "c5.24xlarge")
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            jmeter_node_type=$selection
            break
        fi     
    done
    echo "[$coloredLoading]Loading your account keypairs..."
    ~/amazon-redshift-infrastructure-automation/scripts/bash-menu-cli-commands.sh
    readarray -t list < keypairlist.txt
    number=$(wc -l < keypairlist.txt)
        PS3='[Input Required] Please select the keypair for Jmeter: '
        if [ $number = "0" ]; 
        then 
            read -p "$coloredQuestion[Input Required] Your selected region has no account keypairs. Please enter a name for one: " key_name
        else
            select selection in "${list[@]}"; do
            key_name=$selection
            break
            done
        fi
        echo "You have choosen $selection"
fi

PS3='[Input Required][REGION] Please select your region: '
    options=("us-east-1" "us-east-2" "us-west-1" "us-west-2")
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
        echo $REPLY $selection
            current_region=$selection
            break
        fi     
    done
read -p "$coloredQuestion[Input Required] Enter a stack name: " stack
read -p "$coloredQuestion[Input Required] Enter your on prem CIDR range (format xxx.xxx.xxx.xxx/xx): " onprem_cidr
JSON_STRING=$( jq -n \
                  --arg bn "$vpc_id" \
                  --arg on "$redshift_endpoint" \
                  --arg tl "$dms_migration_to_redshift_target" \
                  --arg sct "$sct_on_prem_to_redshift_target" \
                  --arg on "$redshift_endpoint" \
                  --arg ll "$cidr" \
                  --arg la "$number_of_az" \
                  --arg lt "$cidr_mask" \
                  --arg ci "$cluster_identifier" \
                  --arg db "$database_name" \
                  --arg nt "$node_type" \
                  --arg nn "$number_of_nodes" \
                  --arg mu "$master_user_name" \
                  --arg st "$subnet_type" \
                  --arg en "$encryption" \
                  --arg ltd "$loadTPCdata" \
                  --arg dmsST "$dms_subnet_type" \
                  --arg mt "$migration_type" \
                  --arg sdb "$source_db" \
                  --arg se "$source_engine" \
                  --arg ss "$source_schema" \
                  --arg sh "$source_host" \
                  --arg su "$source_user" \
                  --argjson sp "$source_port" \
                  --arg jnt "$jmeter_node_type" \
                  --arg jkn "$key_name" \
                  --arg jm "$jmeter" \
                  '{
                    vpc_id: $bn, 
                    redshift_endpoint: $on,
                    dms_migration_to_redshift_target: $tl,
                    sct_on_prem_to_redshift_target: $sct,  
                    jmeter: $jm,
                    vpc:{
                        vpc_cidr: $ll,
                        number_of_az: $la, 
                        cidr_mask: $lt
                    },
                    redshift:{
                        cluster_identifier: $ci,
                        database_name: $db,
                        node_type: $nt,
                        number_of_nodes: $nn,
                        master_user_name: $mu,
                        subnet_type: $st,
                        encryption: $en,
                        loadTPCdata: $ltd
                    },
                    dms_migration:{
                        subnet_type: $dmsST,
                        migration_type: $mt
                    },
                    external_database:{
                        source_db: $sdb,
                        source_engine: $se,
                        source_schema: $ss,
                        source_host: $sh,
                        source_user: $su,
                        source_port: $sp
                    },
                    other:{
                        key_name: $jkn,
                        jmeter_node_type: $jnt
                    }
                    }' \ >user-config.json ) 





