import boto3
from typing import Any
import json
#from constructs import Construct
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


class DataSharingProducerStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct,
            id: str,
            #cluster: aws_redshift.CfnCluster,
            defaultrole: str,
            datasharing_config: dict,
            stack_log_level: str,
            log_retention=None,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        stackname = id.split('-')[0]

        #database_name = redshift_config.get('database_name')
        #master_user_name = redshift_config.get('master_user_name')
        
        ProducerCluster = datasharing_config.get('producer_cluster_identifier')
        DatashareName = datasharing_config.get('datashare_name')
        ProducerClusterDb = datasharing_config.get('producer_database_name')
        ProducerClusterMasterUser = datasharing_config.get('producer_username')
        ProducerSchemaName = datasharing_config.get('producer_schema_name')
        ConsumerCluster = datasharing_config.get('consumer_cluster_identifier')
        ConsumerClusterDb = datasharing_config.get('consumer_database_name')
        ConsumerClusterMasterUser = datasharing_config.get('consumer_username')

        client = boto3.client('redshift-data')
        boto_client = boto3.client('redshift')
        #f = open('./scripts/loadTPcH3TB.txt')

        #a = f.read()
        consumer_namespace = (boto_client.describe_clusters(ClusterIdentifier=ConsumerCluster)['Clusters'][0]['ClusterNamespaceArn']).split(":")[6]
        #producer_namespace = (boto_client.describe_clusters(ClusterIdentifier=ProducerCluster)['Clusters'][0]['ClusterNamespaceArn']).split( ":")[6]
        default_role = defaultrole
        #cluster_identifier = cluster.ref

        policy = AwsCustomResourcePolicy.from_sdk_calls(
            resources=AwsCustomResourcePolicy.ANY_RESOURCE)
        lambda_role = self.get_provisioning_lambda_role(construct_id=id)
        # lambda_role.add_to_policy(actions=["redshift:GetClusterCredentials"], resources=['*'])
        lambda_role.add_to_policy(iam.PolicyStatement(actions=["redshift:GetClusterCredentials"], resources=['*']))

        producer_statement = "CREATE DATASHARE " + DatashareName + "; ALTER DATASHARE " + DatashareName + " ADD SCHEMA " + ProducerSchemaName + "; ALTER DATASHARE " + DatashareName + " ADD ALL TABLES IN SCHEMA " +  ProducerSchemaName + "; ALTER DATASHARE " +  DatashareName + " SET INCLUDENEW = TRUE FOR SCHEMA " + ProducerSchemaName + "; GRANT USAGE ON DATASHARE " +  DatashareName + " TO NAMESPACE '" + consumer_namespace + "';"

        create_params = {
            "Database": ProducerClusterDb,
            "Sql": producer_statement,
            "ClusterIdentifier": ProducerCluster,
            "DbUser": ProducerClusterMasterUser
        }
        aws_custresource = AwsCustomResource(self,
                                             id=f'{id}-AWSCustomResource',
                                             policy=policy,
                                             log_retention=log_retention,
                                             on_update=AwsSdkCall(
                                                action='executeStatement',
                                                service='RedshiftData',
                                                parameters=create_params,
                                                physical_resource_id=PhysicalResourceId.of(
                                                                ProducerCluster),
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