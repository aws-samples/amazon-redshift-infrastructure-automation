#!/usr/bin/env python3

import aws_cdk as cdk
import os
import json
# import boto3

from datagencodebase.datagencodebase_stack import DatagencodebaseStack

app = cdk.App()

# my_region = boto3.session.Session().region_name
# account_id = boto3.client('sts').get_caller_identity().get('Account')
# env = {'account': account_id, 'region': my_region}

# outputbucket = os.getenv('outputBucket')
# schemabucket = os.getenv('schemaBucket')
# key = os.getenv('key')
# datarequesttype = os.getenv('data_request_type')
# inschema = os.getenv('in_schema')
# datarequestsize = os.getenv('data_request_size')

# outputbucket = "faker-data-generation"
# schemabucket = "aarete-poc"
# key = "testschema.json"
# datarequesttype = "iot"
# inschema = 'Y'
# datarequestsize = "100000"

config = json.load(open("/home/cloudshell-user/amazon-redshift-infrastructure-automation/datagen/user-config.json"))

outputbucket = config.get('s3_bucket_name')
schemabucket = config.get('schema_bucket')
key = config.get('output_file_type')
datarequesttype = config.get('schema_type')
inschema = config.get('schema_exists')
datarequestsize = config.get('num_records')

# DatagencodebaseStack(app,
#                      "datagencodebase")

DatagencodebaseStack(app,
                     "datagencodebase",
                     # env=env,
                     outputbucket=outputbucket,
                     schemabucket=schemabucket,
                     key=key,
                     datarequesttype=datarequesttype,
                     inschema=inschema,
                     datarequestsize=datarequestsize)

app.synth()
