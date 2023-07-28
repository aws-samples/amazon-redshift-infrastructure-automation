schema_exists=""
schema_bucket=""
schema_type=""
output_file_type=""
num_records=""
s3_bucket_name=""

read -r -p "Do you have an existing schema? (Yy/Nn): " schema_exists
    case $schema_exists in
        [Yy]* ) read -r -p "What is the existing schema bucket's name? " schema_bucket;;
        [Nn]* ) echo
            echo "You have chosen that you don't have an existing schema.";;
        * ) echo "Please answer Y or N.";;
    esac

echo

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

echo
read -r -p "[Number of Records Details]: How many records do you want to generate? " num_records
echo
read -r -p "[S3 Bucket Details]: Please provide the name of the S3 bucket where you want to upload the generated data files: " s3_bucket_name

echo "ADDING TO JSON"

JSON_STRING=$( jq -n \
                  --arg se "$schema_exists" \
                  --arg sb "$schema_bucket" \
                  --arg st "$schema_type" \
                  --arg oft "$output_file_type" \
                  --arg nr "$num_records" \
                  --arg bn "$s3_bucket_name" \
                  '{
                    schema_exists: $se,
                    schema_bucket: $sb,
                    schema_type: $st, 
                    output_file_type: $oft,
                    num_records: $nr,
                    s3_bucket_name: $bn
                    }' \ >user-config.json )

echo "FINISHED ADDING TO JSON"