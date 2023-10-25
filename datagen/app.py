#!/usr/bin/env python3

import aws_cdk as cdk
import json
import boto3
from datagencodebase.datagencodebase_stack import DatagencodebaseStack

app = cdk.App()

my_region = boto3.session.Session().region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')
env = {'account': account_id, 'region': my_region}
# print(env)

config = json.load(open("user-config.json"))

outputbucket = config.get('s3_bucket_name')
schemabucket = config.get('schema_bucket')
key = config.get('schema_key')
outputfiletype = config.get('output_file_type')
datarequesttype = config.get('schema_type')
inschema = config.get('schema_exists')
datarequestsize = config.get('num_records')

DatagencodebaseStack(app,
                     "datagencodebase",
                     env=env,
                     outputbucket=outputbucket,
                     schemabucket=schemabucket,
                     key=key,
                     datarequesttype=datarequesttype,
                     inschema=inschema,
                     datarequestsize=datarequestsize,
                     outputfiletype=outputfiletype
                     )

app.synth()