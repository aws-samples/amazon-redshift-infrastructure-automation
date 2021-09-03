from aws_cdk import aws_dms
from aws_cdk import aws_iam
from aws_cdk import core
import boto3
import json

class GlobalArgs():
    """
    Helper to define global statics
    """

    OWNER = "Redshift POC SSA team"
    ENVIRONMENT = "development"
    REPO_NAME = "redshift-demo"
    SOURCE_INFO = f"https://github.com/kaklis/RedshiftPOCAutomation"
    VERSION = "2021_03_15"
    SUPPORT_EMAIL = ["aws-redshift-poc-sa-amer@amazon.com"]

class DmsInstanceStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct, id: str,
        vpc,
        stack_log_level: str,
        **kwargs

    ) -> None:
        super().__init__(scope, id, **kwargs)

        # DMS IAM Role
        self.dms_vpc_role()
        self.dms_cloudwatch_logs_role()
        self.dms_access_for_endpoint()

        #
        # try:
        #     dms_vpc_role = aws_iam.ManagedPolicy.from_aws_managed_policy_name("dms-vpc-role")
        # except:
        #     dms_vpc_role = aws_iam.Role(
        #       self, "dmsvpcrole",
        #       assumed_by=aws_iam.ServicePrincipal(
        #           "dms.amazonaws.com"),
        #       managed_policies=[
        #           aws_iam.ManagedPolicy.from_aws_managed_policy_name(
        #               "AmazonDMSVPCManagementRole"
        #           )
        #       ],
        #       role_name = "dms-vpc-role"
        #   )

        subnets = vpc.get_vpc_private_subnet_ids

        dms_subnet_group = aws_dms.CfnReplicationSubnetGroup(
            self,
            "DMSsubnetgroup",
            replication_subnet_group_description="Subnet group for DMS replication instance",
            subnet_ids=subnets
         )

        security_group_id = vpc.get_vpc_security_group_id

        self.dms_instance = aws_dms.CfnReplicationInstance(
            self,
            "DMSInstance",
            replication_instance_class="dms.t3.medium",
            allocated_storage=50,
            allow_major_version_upgrade=None,
            auto_minor_version_upgrade=None,
            multi_az=False,
            publicly_accessible=True,
            replication_subnet_group_identifier=dms_subnet_group.ref,
            vpc_security_group_ids=[security_group_id]
        )

    def dms_vpc_role(self):
        client = boto3.client('iam')
        try:
            response = client.get_role(RoleName='dms-vpc-role')
        except:
            try:
                role_policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": [
                                    "dms.amazonaws.com"
                                ]
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
                client.create_role(
                    RoleName='dms-vpc-role',
                    AssumeRolePolicyDocument=json.dumps(role_policy_document)
                )
                client.attach_role_policy(
                    RoleName='dms-vpc-role',
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonDMSVPCManagementRole'
                )
            except Exception as e:
                print(e)

    def dms_cloudwatch_logs_role(self):
        client = boto3.client('iam')
        try:
            response = client.get_role(RoleName='dms-cloudwatch-logs-role')
        except:
            try:
                role_policy_document = {
                       "Version": "2012-10-17",
                       "Statement": [
                       {
                         "Effect": "Allow",
                         "Principal": {
                            "Service": "dms.amazonaws.com"
                         },
                       "Action": "sts:AssumeRole"
                       }
                    ]
                }
                client.create_role(
                    RoleName='dms-cloudwatch-logs-role',
                    AssumeRolePolicyDocument=json.dumps(role_policy_document)
                )
                client.attach_role_policy(
                    RoleName='dms-cloudwatch-logs-role',
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonDMSCloudWatchLogsRole'
                )
            except Exception as e:
                print(e)

    def dms_access_for_endpoint(self):
        client = boto3.client('iam')
        try:
            response = client.get_role(RoleName='dms-access-for-endpoint')
        except:
            try:
                role_policy_document = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "1",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "dms.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        },
                        {
                            "Sid": "2",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "redshift.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
                client.create_role(
                    RoleName='dms-access-for-endpoint',
                    AssumeRolePolicyDocument=json.dumps(role_policy_document)
                )
                client.attach_role_policy(
                    RoleName='dms-access-for-endpoint',
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AmazonDMSRedshiftS3Role'
                )
            except Exception as e:
                print(e)

    @property
    def get_repinstance_id(self):
        return self.dms_instance.ref
