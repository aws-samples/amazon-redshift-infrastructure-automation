aws ec2 --output text --query 'Vpcs[*].{VpcId:VpcId}' describe-vpcs > vpclist.txt

aws redshift --output text --query 'Clusters[*].{Endpoint:Endpoint.Address}' describe-clusters > redshiftlist.txt
