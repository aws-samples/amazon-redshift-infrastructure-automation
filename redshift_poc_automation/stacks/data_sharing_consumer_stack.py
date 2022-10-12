import boto3
from typing import Any
import json
# from constructs import Construct
from aws_cdk import (
    core,
    aws_iam as iam,
    aws_redshift as aws_redshift
)

from aws_cdk.custom_resources import (
    AwsCustomResource,
    AwsCustomResourcePolicy,
    AwsSdkCall,
    PhysicalResourceId,
)


class DataSharingConsumerStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct,
            id: str,
            # cluster: aws_redshift.CfnCluster,
            defaultrole: str,
            # redshift_config: dict,
            stack_log_level: str,
            log_retention=None,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        stackname = id.split('-')[0]

        # database_name = redshift_config.get('database_name')
        # master_user_name = redshift_config.get('master_user_name')
        
        DatashareName = datasharing_config.get('datashare_name')
        ProducerCluster = datasharing_config.get('producer_cluster_identifier')
        ProducerClusterDb = datasharing_config.get('producer_database_name')
        ProducerClusterMasterUser = datasharing_config.get('producer_username')
        ProducerSchemaName = datasharing_config.get('producer_schema_name')
        ConsumerCluster = datasharing_config.get('consumer_cluster_identifier')
        ConsumerClusterDb = datasharing_config.get('consumer_database_name')
        ConsumerClusterMasterUser = datasharing_config.get('consumer_username')

        client = boto3.client('redshift-data')
        boto_client = boto3.client('redshift')
        # f = open('./scripts/loadTPcH3TB.txt')

        # a = f.read()
        consumer_namespace = (boto_client.describe_clusters(ClusterIdentifier='consumer-cluster')['Clusters'][0][
            'ClusterNamespaceArn']).split(":")[6]
        producer_namespace = (boto_client.describe_clusters(ClusterIdentifier='producer-cluster')['Clusters'][0][
            'ClusterNamespaceArn']).split(":")[6]
        default_role = defaultrole
        # cluster_identifier = cluster.ref

        policy = AwsCustomResourcePolicy.from_sdk_calls(
            resources=AwsCustomResourcePolicy.ANY_RESOURCE)
        lambda_role = self.get_provisioning_lambda_role(construct_id=id)
        # lambda_role.add_to_policy(actions=["redshift:GetClusterCredentials"], resources=['*'])
        lambda_role.add_to_policy(iam.PolicyStatement(actions=["redshift:GetClusterCredentials"], resources=['*']))

        consumer_statement = "CREATE DATABASE myconsumer_db FROM DATASHARE " + DatashareName + " OF NAMESPACE '" + producer_namespace + "'; CREATE EXTERNAL SCHEMA myconsumer_schema FROM REDSHIFT DATABASE myconsumer_db SCHEMA " + ProducerSchemaName + "; CREATE SCHEMA myview_schema;CREATE VIEW myview_schema.tickit_sales AS SELECT * FROM myconsumer_schema.tickit_sales WITH NO SCHEMA BINDING;"

        create_params = {
            "Database": ConsumerClusterDb,
            "Sql": consumer_statement,
            "ClusterIdentifier": ConsumerCluster,
            "DbUser": ConsumerClusterMasterUser
        }

        aws_custresource_con = AwsCustomResource(self,
                                                 id=f'{id}-AWSCustomResource',
                                                 policy=policy,
                                                 log_retention=log_retention,
                                                 on_update=AwsSdkCall(
                                                     action='executeStatement',
                                                     service='RedshiftData',
                                                     parameters=create_params,
                                                     physical_resource_id=PhysicalResourceId.of(
                                                         ConsumerCluster),
                                                 ),
                                                 role=lambda_role)

    def get_provisioning_lambda_role(self, construct_id: str):
        return iam.Role(
            scope=self,
            id=f'{construct_id}-LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole")],
        )