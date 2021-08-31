#!/usr/bin/env python3


import json
import boto3
import os
from aws_cdk import core
from redshift_poc_automation.stacks.vpc_stack import VpcStack
from redshift_poc_automation.stacks.redshift_stack import RedshiftStack
from redshift_poc_automation.stacks.redshift_bootstrap_stack import RedshiftBootstrapStack
from redshift_poc_automation.stacks.glue_crawler_stack import GlueCrawlerStack
from redshift_poc_automation.stacks.dms_on_prem_to_redshift_stack import DmsOnPremToRedshiftStack
from redshift_poc_automation.stacks.sct_stack import SctOnPremToRedshiftStack
from redshift_poc_automation.stacks.dmsinstance_stack import DmsInstanceStack

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

redshift_bootstrap_script_s3_path = "N/A"

redshift_what_if = "N/A"
redshift_what_if_config = "N/A"

dms_instance_private_endpoint = config.get('dms_instance_private_endpoint')

dms_on_prem_to_redshift_target = config.get('dms_on_prem_to_redshift_target')
sct_on_prem_to_redshift_target = config.get('sct_on_prem_to_redshift_target')
dms_on_prem_to_redshift_config = config.get('dms_on_prem_to_redshift')
sct_on_prem_to_redshift_config = config.get('sct_on_prem_to_redshift')

glue_crawler_s3_target = "N/A"
glue_crawler_s3_config = "N/A"

stackname = os.getenv('STACK_NAME')
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

if redshift_bootstrap_script_s3_path != "N/A":

    redshift_bootstrap_stack = RedshiftBootstrapStack(
        app,
        f"{stackname}-redshift-bootstrap-stack",
        env=env,
        redshift=redshift_stack,
        redshift_bootstrap_script_s3_path=redshift_bootstrap_script_s3_path,
        stack_log_level="INFO",
        description="AWS Analytics Automation: Deploy Bootstrap Script in Redshift cluster"
    )
    redshift_bootstrap_stack.add_dependency(redshift_stack);

if redshift_what_if != "N/A":
    number_of_clusters = len(redshift_what_if_config.get('configurations'))
    for i in range(len(redshift_what_if_config.get('configurations'))):
        redshift_config={
                        "cluster_identifier": redshift_what_if_config.get('cluster_identifier') + "-" + str(i),
                        "database_name": redshift_what_if_config.get('database_name'),
                        "master_user_name": redshift_what_if_config.get('master_user_name'),
                        "subnet_type": redshift_what_if_config.get('subnet_type'),
                        "node_type": redshift_what_if_config.get('configurations')[i].get('node_type'),
                        "number_of_nodes": redshift_what_if_config.get('configurations')[i].get('number_of_nodes')
        }
        print(redshift_config)
        redshift_what_if_stack = RedshiftStack(
            app,
            f"{stackname}-redshift-what-if-stack-" + str(i),
            env=env,
            vpc=vpc_stack,
            redshift_endpoint="CREATE",
            redshift_config=redshift_config,
            stack_log_level="INFO",
            description="AWS Analytics Automation: Deploy Redshift cluster"
        )
        redshift_what_if_stack.add_dependency(vpc_stack);

        redshift_what_if_bootstrap_stack = RedshiftBootstrapStack(
            app,
            f"{stackname}-redshift-bootstrap-stack-" + str(i),
            env=env,
            redshift=redshift_what_if_stack,
            redshift_bootstrap_script_s3_path=redshift_what_if_config.get('redshift_bootstrap_script_s3_path'),
            stack_log_level="INFO",
            description="AWS Analytics Automation: Deploy Bootstrap Script in Redshift cluster"
        )
        redshift_what_if_bootstrap_stack.add_dependency(redshift_what_if_stack);

# DMS Instance Stack
if dms_instance_private_endpoint == "CREATE":
    dms_instance_stack = DmsInstanceStack(
     app,
     f"{stackname}-dmsinstance-stack",
     env=env,
     vpc=vpc_stack,
     stack_log_level="INFO",
     description="AWS Analytics Automation: DMS Replication Instance"
    )
    dms_instance_stack.add_dependency(vpc_stack);

# DMS OnPrem to Redshift Stack for migrating database to redshift
if dms_on_prem_to_redshift_target == "CREATE":
    dms_on_prem_to_redshift_stack = DmsOnPremToRedshiftStack(
        app,
        f"{stackname}-dms-stack",
        env=env,
        dmsinstance=dms_instance_stack,
        cluster=redshift_stack,
        dmsredshift_config=dms_on_prem_to_redshift_config,
        stack_log_level="INFO",
        description="AWS Analytics Automation: DMS endpoints and tasks"
    )
    dms_on_prem_to_redshift_stack.add_dependency(redshift_stack);
    dms_on_prem_to_redshift_stack.add_dependency(dms_instance_stack);

# SCT OnPrem to Redshift Stack for migrating database to redshift
if sct_on_prem_to_redshift_target == "CREATE":
    sct_on_prem_to_redshift_stack = SctOnPremToRedshiftStack(
        app,
        f"{stackname}-sct-stack",
        env=env,
        cluster=redshift_stack,
        dmsredshift_config=dms_on_prem_to_redshift_config,
        sctredshift_config=sct_on_prem_to_redshift_config,
        redshift_config=redshift_config,
        vpc=vpc_stack,
        stack_log_level="INFO",
        description="AWS Analytics Automation: SCT install on new EC2 Instance"
    )
    sct_on_prem_to_redshift_stack.add_dependency(redshift_stack);

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
