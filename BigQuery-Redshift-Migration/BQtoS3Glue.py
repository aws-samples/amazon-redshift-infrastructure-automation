import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pprint import pprint
import boto3
from boto3.dynamodb.conditions import Key
import json
import datetime
from decimal import Decimal

aws_session = boto3.Session()
client = aws_session.client('s3')
glue = boto3.client('glue')
gluejobname="bq-s3-mig"

args = getResolvedOptions(sys.argv, ["JOB_NAME", 'tablename', 'connectionname'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

bucket = 'bigquery-migration-bucket'
import_tablename = args['tablename']
import_connectionname = args['connectionname']

in_import_tablename = import_tablename.split(".",1)[1]
in_import_tablename_db = import_tablename.split(".")[2]

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('bq_to_s3_tracking_v4')

if in_import_tablename.replace('/','') == 'employee.metadata_table':            ## Update this to generic table name and folder names
    v_filepath = 's3://bigquery-migration-bucket/metadata-table-data/' + in_import_tablename + '/'
else:
    v_filepath = 's3://s3loadertest-useast1/s3-redshift-loader-source/' + in_import_tablename + '/'

table.update_item(
Key={
    'table_name': in_import_tablename_db
},
UpdateExpression="set updated_date = :r, load_status = :p, s3_path = :q",
ExpressionAttributeValues={
    ':r': str(datetime.datetime.now()),
    ':p': 'running',
    ':q': v_filepath
},
ReturnValues="UPDATED_NEW"
)                

# Script generated for node Google BigQuery Connector 0.22.0 for AWS Glue 3.0
GoogleBigQueryConnector0220forAWSGlue30_node1 = (
    glueContext.create_dynamic_frame.from_options(
        connection_type="marketplace.spark",
        connection_options={
            "parentProject": "ultra-unfolding-347804",
            "table": import_tablename,
            "connectionName": import_connectionname,
        },
        transformation_ctx="GoogleBigQueryConnector0220forAWSGlue30_node1",
    )
)

# Script generated for node S3 bucket
S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
    frame=GoogleBigQueryConnector0220forAWSGlue30_node1,
    connection_type="s3",
    format="json",
    connection_options={"path": v_filepath, "partitionKeys": []},
    transformation_ctx="S3bucket_node3",
)

table.update_item(
Key={
    'table_name': in_import_tablename_db
},
UpdateExpression="set updated_date = :r, load_status = :p, s3_path = :q",
ExpressionAttributeValues={
    ':r': str(datetime.datetime.now()),
    ':p': 'completed',
    ':q': v_filepath
},
ReturnValues="UPDATED_NEW"
)  

# update the dynamoDB table for status : Complete or aborted.
job.commit()