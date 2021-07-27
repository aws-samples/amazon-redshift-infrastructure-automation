from aws_cdk import aws_redshift
from aws_cdk import aws_iam
from aws_cdk import aws_secretsmanager
from aws_cdk import core
import json
import boto3
import builtins


class RedshiftStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            vpc,
            redshift_endpoint: str,
            redshift_config: dict,
            stack_log_level: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        if redshift_endpoint != "CREATE":
            ################# todo fix code doesn't work for bootstrap for existing cluster ###########
            redshift_client = boto3.client('redshift')
            cluster_identifier = redshift_endpoint.split('.')[0]
            self.redshift = redshift_client.describe_clusters(ClusterIdentifier=cluster_identifier)['Clusters'][0]
        else:

            cluster_identifier = redshift_config.get('cluster_identifier')
            database_name = redshift_config.get('database_name')
            node_type = redshift_config.get('node_type')
            number_of_nodes = int(redshift_config.get('number_of_nodes'))
            master_user_name = redshift_config.get('master_user_name')
            subnet_type = redshift_config.get('subnet_type')

            # Create Cluster Password  ## MUST FIX EXCLUDE CHARACTERS FEATURE AS IT STILL INCLUDES SINGLE QUOTES SOMETIMES WHICH WILL FAIL
            self.cluster_masteruser_secret = aws_secretsmanager.Secret(
                self,
                "RedshiftClusterSecret",
                description="Redshift Cluster Secret",
                secret_name='RedshiftClusterSecretAA',
                generate_secret_string=aws_secretsmanager.SecretStringGenerator(
                    exclude_punctuation=True, password_length=10),
                removal_policy=core.RemovalPolicy.DESTROY
            )

            # IAM Role for Cluster
            self.cluster_iam_role = aws_iam.Role(
                self, "redshiftClusterRole",
                assumed_by=aws_iam.ServicePrincipal(
                    "redshift.amazonaws.com"),
                managed_policies=[
                    aws_iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonS3ReadOnlyAccess"
                    )
                ]
            )
            self.cluster_masteruser_secret.grant_read(self.cluster_iam_role)

            # Subnet Group for Cluster
            if subnet_type == 'PUBLIC':
                self.cluster_subnet_group = aws_redshift.CfnClusterSubnetGroup(
                    self,
                    "redshiftDemoClusterSubnetGroup",
                    subnet_ids=vpc.get_vpc_public_subnet_ids,
                    description="Redshift Demo Cluster Subnet Group"
                )
            else:
                self.cluster_subnet_group = aws_redshift.CfnClusterSubnetGroup(
                    self,
                    "redshiftDemoClusterSubnetGroup",
                    subnet_ids=vpc.get_vpc_private_subnet_ids,
                    description="Redshift Demo Cluster Subnet Group"
                )

            if number_of_nodes > 1:
                clustertype = "multi-node"
            else:
                clustertype = "single-node"
                number_of_nodes = None

            security_group_id = vpc.get_vpc_security_group_id

            self.demo_cluster = aws_redshift.CfnCluster(
                self,
                cluster_identifier,
                db_name=database_name,
                master_username=master_user_name,
                cluster_type=clustertype,
                master_user_password=self.cluster_masteruser_secret.secret_value.to_string(),
                # master_user_password=master_password,
                iam_roles=[self.cluster_iam_role.role_arn],
                node_type=f"{node_type}",
                number_of_nodes=number_of_nodes,
                cluster_subnet_group_name=self.cluster_subnet_group.ref,
                vpc_security_group_ids=[security_group_id]
            )

        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_1 = core.CfnOutput(
            self,
            "RedshiftCluster",
            value=f"{self.demo_cluster.attr_endpoint_address}",
            description=f"RedshiftCluster Endpoint"
        )

        output_2 = core.CfnOutput(
            self,
            "RedshiftClusterPassword",
            value=(
                f"https://console.aws.amazon.com/secretsmanager/home?region="
                f"{core.Aws.REGION}"
                f"#/secret?name="
                f"{self.cluster_masteruser_secret.secret_arn}"
            ),
            description=f"Redshift Cluster Password in Secrets Manager"
        )
        output_3 = core.CfnOutput(
            self,
            "RedshiftIAMRole",
            value=(
                f"{self.cluster_iam_role.role_arn}"
            ),
            description=f"Redshift Cluster IAM Role Arn"
        )

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
    @property
    def get_cluster(self):
        return self.demo_cluster

    @property
    def get_cluster_dbname(self) -> builtins.str:
        return self.demo_cluster.db_name

    @property
    def get_cluster_user(self) -> builtins.str:
        return self.demo_cluster.master_username

    @property
    def get_cluster_password(self) -> builtins.str:
        return self.demo_cluster.master_user_password

    @property
    def get_cluster_host(self) -> builtins.str:
        return self.demo_cluster.attr_endpoint_address

    @property
    def get_cluster_iam_role(self) -> builtins.str:
        return self.cluster_iam_role.role_arn

    @property
    def get_cluster_secret(self) -> builtins.str:
        return self.cluster_masteruser_secret.secret_name

    ############## FIX bug in CDK. Always returns None #########################
    # @property
    # def get_cluster_identifier(self) -> builtins.str:
    #     return str(self.demo_cluster.cluster_identifier)

    @property
    def get_cluster_availability_zone(self) -> builtins.str:
        return str(self.demo_cluster.availability_zone)