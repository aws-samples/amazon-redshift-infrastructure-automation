aws configure set credential_source Ec2InstanceMetadata
cd apache-jmeter-5.4.1\lib
aws s3 cp s3://event-driven-app-with-lambda-redshift/scripts/redshift-jdbc42-2.0.0.4.jar redshift-jdbc42-2.0.0.4.jar
cd ext
curl -o jmeter-plugins-manager-1.6.jar  https://jmeter-plugins.org/get/jmeter-plugins-manager-1.6.jar
cd ../../..
curl -o openjdk-17.0.1_windows-x64_bin.zip https://download.java.net/java/GA/jdk17.0.1/2a2082e5a09d4267845be086888add4f/12/GPL/openjdk-17.0.1_windows-x64_bin.zip
tar -xf openjdk-17.0.1_windows-x64_bin.zip
cd apache-jmeter-5.4.1/bin
echo set HEAP=-Xms5g -Xmx5g -XX:MaxMetaspaceSize=1g >> jmeter.bat
setx PATH "%PATH%;c:\JMETER\jdk-17.0.1\bin\"
</script>
