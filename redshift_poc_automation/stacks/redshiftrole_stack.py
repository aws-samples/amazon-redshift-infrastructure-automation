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

class RSDefaultRole(Stack):

    def __init__(
            self,
            scope: Construct, id: str,
            cluster: aws_redshift.CfnCluster,
            defaultrole: str,
            stack_log_level: str,
            log_retention=None,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)
        stackname = id.split('-')[0]
           
        default_role=defaultrole
        cluster_identifier=cluster.ref

        policy=AwsCustomResourcePolicy.from_sdk_calls(
            resources=AwsCustomResourcePolicy.ANY_RESOURCE)
        lambda_role = self.get_provisioning_lambda_role(construct_id=id)

        create_params = {
            "ClusterIdentifier": cluster_identifier,
            "DefaultIamRoleArn": default_role
        }

        AwsCustomResource(self,
                          id=f'{id}-AWSCustomResource',
                          policy=policy,
                          log_retention=log_retention,
                          on_update=AwsSdkCall(
                            action='modifyClusterIamRoles',
                            service='Redshift',
                            parameters=create_params,
                            physical_resource_id=PhysicalResourceId.of(
                            cluster_identifier),
                            ),
                          # resource_type='Custom::AWS-S3-Object',
                          role=lambda_role)
                          # You can set the lambda Timeout by passing the Timeout (Default: Duration.minutes(2)


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
   
