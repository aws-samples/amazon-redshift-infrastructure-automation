<script>
set PATH="c:\Program Files\Amazon\AWSCLIV2\";%PATH%
aws configure set role_arn arn:aws:iam::962393875414:role/windows-cli-admin
aws configure set credential_source Ec2InstanceMetadata
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/sctcliauto.scts sctcliauto.scts
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/sctrun.sh sctrun.sh
mkdir Drivers
cd Drivers
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/mssql-jdbc-7.4.1.jre8.jar mssql-jdbc-7.4.1.jre8.jar
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/redshift-jdbc42-2.0.0.4.jar redshift-jdbc42-2.0.0.4.jar
</script>
