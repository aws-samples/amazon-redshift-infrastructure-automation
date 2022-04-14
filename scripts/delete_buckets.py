import boto3
import json
import os

stackname = os.getenv('STACK_NAME')

region_name = boto3.session.Session().region_name
session = boto3.session.Session()
sm_client = session.client(
    service_name='s3',
    region_name=region_name,
)
s3 = boto3.resource('s3')
response = sm_client.list_buckets()

for bucket in response['Buckets']:
    if 'cdktoolkit' in bucket['Name']:
      x = bucket['Name']
      print(x)
      bucket = s3.Bucket(x)
      bucket.objects.all().delete()
      bucket.delete()
