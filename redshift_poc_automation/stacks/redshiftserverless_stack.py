from aws_cdk import aws_redshiftserverless
from aws_cdk import aws_iam
from aws_cdk import aws_secretsmanager
from aws_cdk import core
from aws_cdk import aws_ec2
import json
import boto3
from redshift_poc_automation.stacks.redshiftrole_stack import RSDefaultRole
from redshift_poc_automation.stacks.redshiftload_stack import RedshiftLoadStack
import builtins
import getpass


class RedshiftServerlessStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            vpc,
            redshift_serverless_endpoint: str,
            redshift_serverless_config: dict,
            stack_log_level: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        stackname = id.split('-')[0]
        redshift_serverless_client = boto3.client('redshift-serverless')

        if redshift_serverless_endpoint != "CREATE":
            #ToDo:
            ec2_client = boto3.resource('ec2')
            cluster_identifier = redshift_serverless_endpoint.split('.')[0]
            self.redshift = redshift_serverless_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
            
            self.password = stackname+'-RedshiftPassword'
            
            region_name = boto3.session.Session().region_name
            session = boto3.session.Session()
            client = session.client(
                    service_name='secretsmanager',
                    region_name=region_name,
                )

            try:
                source_pwd = client.get_secret_value(
                    SecretId=stackname+'-RedshiftPassword'
                )['SecretString']
            except Exception:
                source_pwd = getpass.getpass(prompt='Redshift serverless cluster password: ')
                client.create_secret(
                    Name=stackname+'-RedshiftPassword',
                    SecretString=source_pwd,
                    Description='Password of Redshift cluster'
                )

            redshift_sg_id = self.redshift['VpcSecurityGroups'][0]['VpcSecurityGroupId']
            redshift_sg_name = ec2_client.SecurityGroup(redshift_sg_id).group_name

            redshift_sg = aws_ec2.SecurityGroup.from_security_group_id(self, redshift_sg_name, redshift_sg_id)

            dms_sg = vpc.get_vpc_security_group
            redshift_sg.add_ingress_rule(peer=dms_sg, connection=aws_ec2.Port.all_traffic(), description="DMS input.")

        else:

            namespace_name = redshift_serverless_config.get('namespace_name')
            workgroup_name = redshift_serverless_config.get('workgroup_name')
            base_capacity = redshift_serverless_config.get('base_capacity')
            ##admin_user_name = redshift_serverless_config.get('admin_user_name')
            ##admin_user_password = redshift_serverless_config.get('admin_user_password')
            database_name = redshift_serverless_config.get('database_name')

            # Create Cluster Password  ## MUST FIX EXCLUDE CHARACTERS FEATURE AS IT STILL INCLUDES SINGLE QUOTES SOMETIMES WHICH WILL FAIL
            #self.cluster_masteruser_secret = aws_secretsmanager.Secret(
            #    self,
            #    "RedshiftClusterSecret",
            #    description="Redshift Cluster Secret",
            #    secret_name=stackname+'-RedshiftClusterSecretAA',
            #    generate_secret_string=aws_secretsmanager.SecretStringGenerator(
            #        exclude_punctuation=True, password_length=10),
            #    removal_policy=core.RemovalPolicy.DESTROY
            #)

            # IAM Role for Cluster
            self.cluster_iam_role = aws_iam.Role(
                self, "redshiftServerlessClusterRole",
                assumed_by=aws_iam.ServicePrincipal(
                    "redshift.amazonaws.com"),
                description="Added by Redshift Infrastructure Automation Toolkit",
                managed_policies=[
                    aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonS3ReadOnlyAccess"
                    ),
                    aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonRedshiftFullAccess"
                    )
                ]
            )
            #self.cluster_masteruser_secret.grant_read(self.cluster_iam_role)

            security_group_id = vpc.get_vpc_security_group_id

            self.public_subnet_ids = vpc.get_vpc_public_subnet_ids

            # self.private_subnet_ids = vpc.get_vpc_private_subnet_ids

            self.namespace = aws_redshiftserverless.CfnNamespace(self, "MyCfnNamespace",
                                                            namespace_name=namespace_name,

                                                            # the properties below are optional
                                                            #admin_username=admin_user_name,
                                                            #admin_user_password=admin_user_password,
                                                            db_name=database_name,
                                                            #default_iam_role_arn=self.cluster_iam_role.role_arn,
                                                            iam_roles=[self.cluster_iam_role.role_arn]
                                                            )

            #time.sleep(3)

            self.workgroup = aws_redshiftserverless.CfnWorkgroup(self, "MyCfnWorkgroup",
                                                            workgroup_name=workgroup_name,

                                                            # the properties below are optional
                                                            base_capacity=base_capacity,
                                                            namespace_name=namespace_name,
                                                            #publicly_accessible=False,
                                                            subnet_ids=self.public_subnet_ids,
                                                            security_group_ids=[security_group_id]
                                                            )
            self.workgroup.add_depends_on(self.namespace)


        ###########################################
        ################# OUTPUTS #################
        ###########################################
#         output_1 = core.CfnOutput(
#             self,
#             "RedshiftCluster",
#             value=f"{self.demo_cluster.attr_endpoint_address}",
#             description=f"RedshiftCluster Endpoint"
#         )

#         output_2 = core.CfnOutput(
#             self,
#             "RedshiftClusterPassword",
#             value=(
#                 f"https://console.aws.amazon.com/secretsmanager/home?region="
#                 f"{core.Aws.REGION}"
#                 f"#/secret?name="
#                 f"{self.cluster_masteruser_secret.secret_arn}"
#             ),
#             description=f"Redshift Cluster Password in Secrets Manager"
#         )
#         output_3 = core.CfnOutput(
#             self,
#             "RedshiftIAMRole",
#             value=(
#                 f"{self.cluster_iam_role.role_arn}"
#             ),
#             description=f"Redshift Cluster IAM Role Arn"
#         )

        ############## FIX bug in CDK. Always returns None #########################

        # output_4 = core.CfnOutput(
        #     self,
        #     "RedshiftClusterIdentifier",
        #     value=(
        #         f"{self.demo_cluster.cluster_identifier}"
        #     ),
        #     description=f"Redshift Cluster Identifier"
        # )

    # properties to share with other stacks 
    # IMPORTANT: these methods are for Redshift Provisioned only
    @property
    def get_cluster(self):
        if type(self.redshift) == dict:  ##needed for dms
            return self.redshift
        return self.redshift
    
    @property
    def get_cluster_type(self):
        return (type(self.redshift) == dict)  #needed dms

    @property
    def get_cluster_dbname(self) -> builtins.str: #needed dms
        if type(self.redshift) == dict:
            return self.redshift['DBName']
        return self.redshift.db_name        

    @property
    def get_cluster_user(self) -> builtins.str: #needed dms
        if type(self.redshift) == dict:
            return self.redshift['MasterUsername']
        return self.redshift.master_username

    @property
    def get_cluster_password(self) -> builtins.str: #needed dms
        return self.redshift.master_user_password

    @property
    def get_cluster_host(self) -> builtins.str: #needed dms
        if type(self.redshift) == dict:
            return self.redshift['Endpoint']['Address']
        return self.redshift.attr_endpoint_address

    @property
    def get_cluster_iam_role(self) -> builtins.str:
        if type(self.redshift) == dict:
            return self.redshift['IamRoles'][0]['IamRoleArn']
        return self.cluster_iam_role.role_arn

    @property
    def get_cluster_secret(self) -> builtins.str:
        if type(self.redshift) == dict:
            return self.password
        return self.cluster_masteruser_secret.secret_name

    ############## FIX bug in CDK. Always returns None #########################
    @property
    def get_cluster_endpoint(self) -> builtins.str:
        return str(self.redshift.attr_endpoint_address)

    @property
    def get_cluster_identifier(self) -> builtins.str:
        return str(self.redshift.attr_endpoint_address).split('.')[0]

    @property
    def get_cluster_availability_zone(self) -> builtins.str:
        if type(self.redshift) == dict:
            return self.redshift['AvailabilityZone']
        return str(self.redshift.availability_zone)
