import boto3
from typing import Any
from aws_cdk import (
    aws_iam as iam,
    aws_redshift as aws_redshift
)
    
from aws_cdk.custom_resources import (
    AwsCustomResource,
    AwsCustomResourcePolicy,
    AwsSdkCall,
    PhysicalResourceId,
)

from aws_cdk import Stack
from constructs import Construct

class RedshiftLoadStack(Stack):

    def __init__(
            self,
            scope: Construct, id: str,
            cluster: aws_redshift.CfnCluster,
            defaultrole: str,
            redshift_config: dict,
            stack_log_level: str,
            log_retention=None,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        stackname = id.split('-')[0]
        
        database_name = redshift_config.get('database_name')
        master_user_name = redshift_config.get('master_user_name')
        
        client = boto3.client('redshift-data')
        f = open('./scripts/loadTPcH3TB.txt')

        a = f.read()
        
        default_role=defaultrole
        cluster_identifier=cluster.ref

        policy=AwsCustomResourcePolicy.from_sdk_calls(
            resources=AwsCustomResourcePolicy.ANY_RESOURCE)
        lambda_role = self.get_provisioning_lambda_role(construct_id=id)
        #lambda_role.add_to_policy(actions=["redshift:GetClusterCredentials"], resources=['*'])
        lambda_role.add_to_policy(iam.PolicyStatement(actions=["redshift:GetClusterCredentials"], resources=['*']))

        create_params = {
            "Database": database_name,
            "Sql": a, 
            "ClusterIdentifier": cluster_identifier,
            "DbUser": master_user_name
        }

        AwsCustomResource(self,
                          id=f'{id}-AWSCustomResource',
                          policy=policy,
                          log_retention=log_retention,
                          on_update=AwsSdkCall(
                            action='executeStatement',
                            service='RedshiftData',
                            parameters=create_params,
                            physical_resource_id=PhysicalResourceId.of(
                            cluster_identifier),
                            ),
                          role=lambda_role)
                          # You can set the lambda Timeout by passing the Timeout (Default: Duration.minutes(2)

        # Closing file
        f.close()

        # api_version=None uses the latest api
        #on_update = AwsSdkCall(
        #    action='modifyClusterIamRoles',
        #    service='Redshift',
        #    parameters=create_params,
        #    physical_resource_id=PhysicalResourceId.of(
        #        cluster_identifier),
        #)
        #return on_update

    def get_provisioning_lambda_role(self, construct_id: str):
        return iam.Role(
            scope=self,
            id=f'{construct_id}-LambdaRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSLambdaBasicExecutionRole")],
        )
