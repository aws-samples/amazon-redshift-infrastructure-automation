from aws_cdk import aws_dms
from aws_cdk import core
from aws_cdk import aws_iam
import boto3
import getpass
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

class DmsOnPremToRedshiftStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct, id: str,
        vpc,
        dmsmigration_config: dict,
        source_config: dict,
        cluster,
        stack_log_level: str,
        **kwargs

    ) -> None:
        super().__init__(scope, id, **kwargs)

        stackname = id.split('-')[0]

        #--------CREATE DMS INSTANCE--------
        subnet_type = dmsmigration_config.get('subnet_type')
        dms_instance_type = dmsmigration_config.get('dms_instance_type')
        
        # DMS IAM Role
        self.dms_vpc_role()
        self.dms_cloudwatch_logs_role()
        self.dms_access_for_endpoint()
        
        publiclyaccessible = False
        if subnet_type == 'PUBLIC':
            subnets = vpc.get_vpc_public_subnet_ids
            publiclyaccessible = True
        elif subnet_type == 'PRIVATE':
            subnets = vpc.get_vpc_private_subnet_ids
        elif subnet_type == 'ISOLATED':
            subnets = vpc.get_vpc_private_isolated_subnet_ids

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
            replication_instance_class=dms_instance_type,
            allocated_storage=50,
            allow_major_version_upgrade=None,
            auto_minor_version_upgrade=None,
            multi_az=False,
            publicly_accessible=publiclyaccessible,
            replication_subnet_group_identifier=dms_subnet_group.ref,
            vpc_security_group_ids=[security_group_id]
        )

        #--------CREATE DMS MIGRATION TASK--------
        source_db = source_config.get('source_db')
        source_engine = source_config.get('source_engine')
        source_schema = source_config.get('source_schema')
        source_host = source_config.get('source_host')
        source_user = source_config.get('source_user')
        source_port = int(source_config.get('source_port'))
        migration_type = dmsmigration_config.get('migration_type')

        secret_name = stackname+"-SourceDBPassword"
        region_name = boto3.session.Session().region_name

        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
        )

        try:
            source_pwd = client.get_secret_value(
                SecretId=secret_name
            )['SecretString']
        except Exception:
            source_pwd = getpass.getpass(prompt='Source DB Password: ')
            client.create_secret(
                Name=secret_name,
                SecretString=source_pwd,
                Description='Source database password for DMS'
            )
            pass

        
        
        if cluster.get_cluster_type:
            target_pwd = client.get_secret_value(
                SecretId=cluster.get_cluster_secret
            )['SecretString']
        else:
            target_pwd = cluster.get_cluster_password

        tablemappings="""{
          "rules": [
            {
              "rule-type": "selection",
              "rule-id": "1",
              "rule-name": "1",
              "object-locator": {
                "schema-name": "%"""+source_schema + """",
                "table-name": "%"
              },
              "rule-action": "include",
              "filters": []
            }
          ]
        }"""

        self.dms_endpoint_tgt = aws_dms.CfnEndpoint(
            self,
            "DMSendpointtgt",
            endpoint_type="target",
            engine_name="redshift",
            database_name=f"{cluster.get_cluster_dbname}",
            password=f"{target_pwd}",
            username=f"{cluster.get_cluster_user}",
            server_name=f"{cluster.get_cluster_host}",
            port=5439
         )

        self.dms_endpoint_src = aws_dms.CfnEndpoint(
            self,
            "DMSendpointsrc",
            endpoint_type="source",
            engine_name=source_engine,
            database_name=source_db,
            password=source_pwd,
            port=source_port,
            username=source_user,
            server_name=source_host,
         )

        dms_task = aws_dms.CfnReplicationTask(
            self,
            "DMSreplicationtask",
            migration_type=migration_type,
            replication_instance_arn=self.dms_instance.ref,
            source_endpoint_arn=self.get_srcendpoint_id,
            target_endpoint_arn=self.get_tgtendpoint_id,
            table_mappings=tablemappings
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
        return self.dms.ref

    @property
    def get_tgtendpoint_id(self):
        return self.dms_endpoint_tgt.ref

    @property
    def get_srcendpoint_id(self):
        return self.dms_endpoint_src.ref
