<script>
echo Current date and time >> %SystemRoot%\Temp\test.log
echo %DATE% %TIME% >> %SystemRoot%\Temp\test.log
cd c:\
mkdir JMETER
cd JMETER
curl -o apache-jmeter-5.4.3.zip  https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.4.3.zip
tar -xf apache-jmeter-5.4.3.zip
curl -o AWSCLIV2.msi https://awscli.amazonaws.com/AWSCLIV2.msi
msiexec.exe /i "AWSCLIV2.msi" /passive /l logcli.txt
set PATH=c:\Program Files\Amazon\AWSCLIV2\;%PATH%
