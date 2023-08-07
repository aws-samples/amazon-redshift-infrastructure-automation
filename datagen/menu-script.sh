schema_exists=""
schema_bucket=""
schema_type=""
output_file_type=""
key=""
batch_size=""
num_records=""
s3_bucket_name=""


existingSchemaDetails (){
read -r -p "Do you have an existing schema? (Yy/Nn): " schema_exists
    case $schema_exists in
        [Yy]* ) read -r -p "What is the existing schema bucket's name? " schema_bucket;;
        [Nn]* ) echo
            echo "You have chosen that you don't have an existing schema.";;
        * ) echo "Please answer Y or N.";;
    esac

echo

if [ "$schema_exists" == "y" ] || [ "$schema_exists" == "Y" ];
then
	~/amazon-redshift-infrastructure-automation/datagen/bash-menu-cli-commands.sh
		list="s3bucketlist.txt"
		if grep -q "$schema_bucket" "$list"; then
			echo "The bucket provided exists."
		else
			echo "The bucket provided does not exist. Please provide a valid bucket name."
			schema_exists="n"
			echo
		fi
	echo
	read -r -p "[Key Details]: Please provide the key path: " key
	echo
fi

if [ "$schema_exists" == "n" ] || [ "$schema_exists" == "N" ];
then 
	PS3='[Schema Details]: Please select a predefined schema: '
		options=("IoT" "Finance")
		select selection in "${options[@]}"; do
			if [[ $REPLY == "0" ]]; then
				echo 'Goodbye' >&2
				exit
			else
				echo
				echo "You have chosen $selection"
				schema_type=$selection
				echo
				break
			fi
		done
fi
}

existingSchemaDetails
# echo 

PS3='[Output File Details]: Please select an output file type: '
    options=("JSON")
    select selection in "${options[@]}"; do
        if [[ $REPLY == "0" ]]; then
            echo 'Goodbye' >&2
            exit
        else
            echo
            echo "You have chosen $selection"
            output_file_type=$selection
            break
        fi     
    done

# echo
# read -r -p "[Key Details]: Please provide the key path: " key
echo
read -r -p "[Batch Size Details]: What is the size of your batch? " batch_size
echo
read -r -p "[Number of Records Details]: How many records do you want to generate? " num_records
echo

outputBucketDetails (){
PS3='[Output S3 Bucket Details]: Would you like to create a new S3 bucket or use an existing one in which the generated data files will be uploaded? '
	options=("Create a new S3 bucket" "Use an existing S3 bucket")
	select selection in "${options[@]}"; do
		if [[ $REPLY == "0" ]]; then
			echo 'Goodbye' >&2
			exit
		elif [[ $REPLY == "1" ]]; then
			echo
			echo "You have chosen $selection"
			echo
			read -r -p  "Enter the name of the new S3 bucket:" s3_bucket_name
			aws s3api  create-bucket --bucket $s3_bucket_name --region us-east-1
			break
		elif [[ $REPLY == "2" ]]; then
			echo
			echo "You have chosen $selection"
			echo
			read -r -p "Please provide the name of the S3 bucket where you want to upload the generated data files: " s3_bucket_name
			~/amazon-redshift-infrastructure-automation/datagen/bash-menu-cli-commands.sh
				list="s3bucketlist.txt"
				if grep -q "$s3_bucket_name" "$list"; then
					echo "The bucket provided exists."
					echo
					break
				else
					echo "The bucket provided does not exist. Please provide a valid bucket name."
					echo
					set -e
					# exit
				fi
		fi
	done
}

outputBucketDetails
echo


JSON_STRING=$( jq -n \
                  --arg se "$schema_exists" \
                  --arg sb "$schema_bucket" \
                  --arg st "$schema_type" \
                  --arg oft "$output_file_type" \
		  --arg key "$key" \
		  --arg bs "$batch_size" \
                  --arg nr "$num_records" \
                  --arg bn "$s3_bucket_name" \
                  '{
                    schema_exists: $se,
                    schema_bucket: $sb,
                    schema_type: $st, 
                    output_file_type: $oft,
		    key: $key,
		    batch_size: $bs,
                    num_records: $nr,
                    s3_bucket_name: $bn
                    }' \ >user-config.json )

