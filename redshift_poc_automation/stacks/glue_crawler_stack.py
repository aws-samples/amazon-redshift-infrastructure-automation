from aws_cdk import aws_glue
from aws_cdk import aws_iam
from aws_cdk import core
import boto3


class GlobalArgs():
    """
    Helper to define global statics
    """
    OWNER = "Manash Deb"
    ENVIRONMENT = "development"
    REPO_NAME = "redshift-demo"
    VERSION = "2021_03_15"


class GlueCrawlerStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            glue_crawler_s3_config,
            stack_log_level: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        account_id = self.account
        iam_role_arn = glue_crawler_s3_config.get('iam_role_arn')
        database_name = glue_crawler_s3_config.get('database_name')
        s3_locations = glue_crawler_s3_config.get('s3_locations')
        s3_paths = [{"path": i} for i in s3_locations]

        if iam_role_arn == "CREATE":
                glue_role = aws_iam.Role(
                    self,
                    'glue_role',
                    assumed_by=aws_iam.ServicePrincipal('glue.amazonaws.com'),
                    managed_policies=[aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSGlueServiceRole')]
                )
                iam_role_arn = glue_role.role_arn

        self.glue_database = aws_glue.CfnDatabase(
            self,
            'glue_database',
            catalog_id=account_id,
            database_input={"name": database_name}
        )

        self.glue_crawler = aws_glue.CfnCrawler(
            self,
            'glue_crawler',
            database_name=database_name,
            role=iam_role_arn,
            targets={
                "s3Targets": s3_paths
            },
        )
