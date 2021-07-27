aws configure set credential_source Ec2InstanceMetadata
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/sctcliauto.scts sctcliauto.scts
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/sctrun.ps1 sctrun.ps1
mkdir Drivers
cd Drivers
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/mssql-jdbc-7.4.1.jre8.jar mssql-jdbc-7.4.1.jre8.jar
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/redshift-jdbc42-2.0.0.4.jar redshift-jdbc42-2.0.0.4.jar
</script>
