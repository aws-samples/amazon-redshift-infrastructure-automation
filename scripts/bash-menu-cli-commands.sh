aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs > list.txt

aws redshift --output text --query 'Clusters[*].{Endpoint:Endpoint.Address}' describe-clusters > test.txt
