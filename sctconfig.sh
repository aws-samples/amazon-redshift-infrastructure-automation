<script>
echo Current date and time >> %SystemRoot%\Temp\test.log
echo %DATE% %TIME% >> %SystemRoot%\Temp\test.log
cd c:\
mkdir SCT
cd SCT
curl -o aws-schema-conversion-tool-1.0.latest.zip  https://s3.amazonaws.com/publicsctdownload/Windows/aws-schema-conversion-tool-1.0.latest.zip
tar -xf aws-schema-conversion-tool-1.0.latest.zip
for /R C:\SCT %# in ("AWS Schema Conversion*.msi") do %SystemRoot%\System32\msiexec.exe /passive /i "%#"
curl -o AWSCLIV2.msi https://awscli.amazonaws.com/AWSCLIV2.msi
msiexec.exe /i "AWSCLIV2.msi" /passive /l logcli.txt
set PATH="c:\Program Files\Amazon\AWSCLIV2\";%PATH%
