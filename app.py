#!/usr/bin/env python3


import json
import boto3
import os
from aws_cdk import core
from redshift_poc_automation.stacks.vpc_stack import VpcStack
from redshift_poc_automation.stacks.redshift_stack import RedshiftStack
from redshift_poc_automation.stacks.redshiftrole_stack import RSDefaultRole
from redshift_poc_automation.stacks.dms_on_prem_to_redshift_stack import DmsOnPremToRedshiftStack
from redshift_poc_automation.stacks.sct_stack import SctOnPremToRedshiftStack
from redshift_poc_automation.stacks.jmeter_stack import JmeterStack

app = core.App()

my_region = boto3.session.Session().region_name
account_id = boto3.client('sts').get_caller_identity().get('Account')
env = {'account': account_id, 'region': my_region}
config = json.load(open("user-config.json"))

# Get the values of the user-config file
vpc_id = config.get('vpc_id')
vpc_config = config.get('vpc')

redshift_endpoint = config.get('redshift_endpoint')
redshift_config = config.get('redshift')

dms_on_prem_to_redshift_target = config.get('dms_migration_to_redshift_target')
sct_on_prem_to_redshift_target = config.get('sct_on_prem_to_redshift_target')
jmeter = config.get('jmeter')
dms_on_prem_to_redshift_config = config.get('dms_migration')
external_database_config = config.get('external_database')
other_config = config.get('other')

stackname = os.getenv('STACK_NAME')

glue_crawler_s3_target = "N/A"
glue_crawler_s3_config = "N/A"

# VPC Stack for hosting secure API & other resources
vpc_stack = VpcStack(
    app,
    f"{stackname}-vpc-stack",
    env=env,
    vpc_id=vpc_id,
    vpc_config=vpc_config,
    stack_log_level="INFO",
    description="AWS Analytics Automation: Custom Multi-AZ VPC"
)

# Deploy Redshift cluster and load data"
if redshift_endpoint != "N/A":

    redshift_stack = RedshiftStack(
        app,
        f"{stackname}-redshift-stack",
        env=env,
        vpc=vpc_stack,
        redshift_endpoint=redshift_endpoint,
        redshift_config=redshift_config,
        stack_log_level="INFO",
        description="AWS Analytics Automation: Deploy Redshift cluster"
    )
    redshift_stack.add_dependency(vpc_stack);
    
    redshiftrole_stack = RSDefaultRole(
      app,
      f"{stackname}-redshiftrole-stack",
      env=env,
      cluster=redshift_stack.redshift,
      defaultrole=redshift_stack.cluster_iam_role.role_arn,
      stack_log_level="INFO",
      description="AWS Analytics Automation: Modify Redshift Role"
    )
    redshiftrole_stack.add_dependency(redshift_stack);

# DMS OnPrem to Redshift Stack for migrating database to redshift
if dms_on_prem_to_redshift_target == "CREATE":
    dms_on_prem_to_redshift_stack = DmsOnPremToRedshiftStack(
        app,
        f"{stackname}-dms-stack",
        env=env,
        vpc = vpc_stack,
        dmsmigration_config = dms_on_prem_to_redshift_config,
        source_config = external_database_config,
        cluster=redshift_stack,
        stack_log_level="INFO",
        description="AWS Analytics Automation: DMS endpoints and tasks"
    )
    dms_on_prem_to_redshift_stack.add_dependency(redshift_stack);

# SCT OnPrem to Redshift Stack for migrating database to redshift
if sct_on_prem_to_redshift_target == "CREATE":
    sct_on_prem_to_redshift_stack = SctOnPremToRedshiftStack(
        app,
        f"{stackname}-sct-stack",
        env=env,
        cluster=redshift_stack,
        other_config=other_config,
        redshift_config=redshift_config,
        vpc=vpc_stack,
        stack_log_level="INFO",
        vpc_config=vpc_config,
        description="AWS Analytics Automation: SCT install on new EC2 Instance"
    )
    sct_on_prem_to_redshift_stack.add_dependency(redshift_stack);

if jmeter == "CREATE":
    jmeter_stack = JmeterStack(
        app,
        f"{stackname}-jmeter-stack",
        env=env,
        cluster=redshift_stack,
        other_config=other_config,
        redshift_config=redshift_config,
        vpc=vpc_stack,
        stack_log_level="INFO",
        vpc_config=vpc_config,
        description="AWS Analytics Automation: Jmeter install on new EC2 Instance"
    )
    jmeter_stack.add_dependency(redshift_stack);

# Glue Crawler Stack to crawl s3 locations
if glue_crawler_s3_target != "N/A":
    glue_crawler_stack = GlueCrawlerStack(
        app,
        f"{stackname}-glue-crawler-stack",
        env=env,
        glue_crawler_s3_config=glue_crawler_s3_config,
        stack_log_level="INFO",
        description="AWS Analytics Automation: Deploy Glue Crawler for S3 data lake"
    )
    glue_crawler_stack.add_dependency(vpc_stack);


# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            core.Tags.of(app).add(k, v, apply_to_launched_instances=True)


app.synth()
