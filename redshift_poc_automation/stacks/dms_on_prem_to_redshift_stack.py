from aws_cdk import aws_dms
from aws_cdk import core
import boto3

class GlobalArgs():
    """
    Helper to define global statics
    """

    OWNER = "Redshift POC SSA team"
    ENVIRONMENT = "development"
    REPO_NAME = "redshift-demo"
    VERSION = "2021_03_15"

class DmsOnPremToRedshiftStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct, id: str,
        dmsinstance,
        cluster,
        dmsredshift_config: dict,
        stack_log_level: str,
        **kwargs

    ) -> None:
        super().__init__(scope, id, **kwargs)

        source_db = dmsredshift_config.get('source_db')
        source_engine = dmsredshift_config.get('source_engine')
        source_schema = dmsredshift_config.get('source_schema')
        source_host = dmsredshift_config.get('source_host')
        source_user = dmsredshift_config.get('source_user')
        # source_pwd = dmsredshift_config.get('source_pwd')
        source_port = int(dmsredshift_config.get('source_port'))
        migration_type = dmsredshift_config.get('migration_type')

        secret_name = "SourceDBPassword"
        region_name = boto3.session.Session().region_name

        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name,
        )

        source_pwd = client.get_secret_value(
            SecretId=secret_name
        )['SecretString']

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
            password=f"{cluster.get_cluster_password}",
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
            replication_instance_arn=dmsinstance.get_repinstance_id,
            source_endpoint_arn=self.get_srcendpoint_id,
            target_endpoint_arn=self.get_tgtendpoint_id,
            table_mappings=tablemappings
        )

    @property
    def get_repinstance_id(self):
        return self.dms.ref

    @property
    def get_tgtendpoint_id(self):
        return self.dms_endpoint_tgt.ref

    @property
    def get_srcendpoint_id(self):
        return self.dms_endpoint_src.ref
