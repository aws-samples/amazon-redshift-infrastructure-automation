from aws_cdk import aws_lambda
from aws_cdk import aws_cloudformation
from aws_cdk import custom_resources
from aws_cdk import aws_iam
from aws_cdk import core
import hashlib


class RedshiftBootstrapStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            redshift,
            redshift_bootstrap_script_s3_path: str,
            stack_log_level: str,
            **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        lambdaRunScriptIamRole = aws_iam.Role(
            self,
            "lambdaRunScriptIamRole",
            assumed_by=aws_iam.ServicePrincipal(
                "lambda.amazonaws.com"),
            managed_policies=[aws_iam.ManagedPolicy.from_managed_policy_arn(self, 'AWSLambdaVPCAccessExecutionRole',
                                                                            'arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole')],
            inline_policies={
                'lambdaRunScriptIamPolicy': aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            actions=[
                                "redshift-data:ExecuteStatement",
                                "redshift-data:ListStatements",
                                "redshift-data:GetStatementResult",
                                "redshift-data:DescribeStatement"
                            ],
                            resources=['*']),
                        aws_iam.PolicyStatement(
                            actions=[
                                "s3:GetObject"
                            ],
                            resources=[redshift_bootstrap_script_s3_path.replace("s3://", "arn:aws:s3:::")]),
                        aws_iam.PolicyStatement(
                            actions=[
                                "redshift:GetClusterCredentials"
                            ],
                            resources=["*"
                                       # "arn:aws:redshift:" + self.region + ":" + self.account + ":cluster:" + redshift.get_cluster_identifier,
                                       # "arn:aws:redshift:" + self.region + ":" + self.account + ":dbname:" + redshift.get_cluster_identifier + "/" + redshift.get_cluster_dbname,
                                       # "arn:aws:redshift:" + self.region + ":" + self.account + ":dbuser:" + redshift.get_cluster_identifier + "/" + redshift.get_cluster_user
                                       ])
                    ]
                )
            }
        )

        with open("lambda_run_redshift_script.py", encoding="utf8") as fp:
            lambda_run_redshift_script_code = fp.read()

        lambda_run_redshift_script = aws_lambda.Function(
            self, "lambdaRunRedshiftScript",
            code=aws_lambda.InlineCode(lambda_run_redshift_script_code),
            handler="index.handler",
            timeout=core.Duration.seconds(60),
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            role=lambdaRunScriptIamRole
            # ,environment={
            #     'ACTION': 'RUN_REDSHIFT_SCRIPT',
            #     'REDSHIFT_HOST': redshift.get_cluster_host,
            #     'REDSHIFT_DB': redshift.get_cluster_dbname,
            #     'REDSHIFT_USER': redshift.get_cluster_user,
            #     'REDSHIFT_IAM_ROLE': redshift.get_cluster_iam_role,
            #     'SCRIPT_S3_PATH': redshift_bootstrap_script_s3_path}
        )

        lambdaCustomResourceCallRunScriptIamRole = aws_iam.Role(
            self,
            "lambdaCustomResourceCallRunScriptIamRole",
            assumed_by=aws_iam.ServicePrincipal(
                "lambda.amazonaws.com"),
            managed_policies=[aws_iam.ManagedPolicy.from_managed_policy_arn(self, 'AWSLambdaRole',
                                                                            'arn:aws:iam::aws:policy/service-role/AWSLambdaRole')],
            inline_policies={
                'lambdaRunScriptIamPolicy': aws_iam.PolicyDocument(
                    statements=[
                        aws_iam.PolicyStatement(
                            actions=[
                                "logs:CreateLogGroup",
                                "logs:CreateLogStream",
                                "logs:PutLogEvents",
                            ],
                            resources=['*']),
                        aws_iam.PolicyStatement(
                            actions=[
                                "s3:GetObject"
                            ],
                            resources=[redshift_bootstrap_script_s3_path.replace("s3://", "arn:aws:s3:::")])
                    ]
                )
            }
        )


        with open("lambda_call_lambda_to_run_redshift_script.py", encoding="utf8") as fp:
            lambda_custom_resource_call_run_redshift_script_code = fp.read()

        lambda_custom_resource_call_run_redshift_script = aws_cloudformation.CustomResource(
            self, "customResourceLambdaCallRunRedshiftScript",
            provider=aws_cloudformation.CustomResourceProvider.lambda_(
                aws_lambda.SingletonFunction(
                    self, "lambdaRunScriptRedshift",
                    code=aws_lambda.InlineCode(lambda_custom_resource_call_run_redshift_script_code),
                    handler="index.handler",
                    timeout=core.Duration.seconds(900),
                    runtime=aws_lambda.Runtime.PYTHON_3_7,
                    role=lambdaCustomResourceCallRunScriptIamRole,
                    uuid=get_md5(self.account, self.region, redshift_bootstrap_script_s3_path)
                )
            ),
            properties={
                'Action': 'RUN_REDSHIFT_SCRIPT',
                'RedshiftHost': redshift.get_cluster_host,
                'RedshiftDb': redshift.get_cluster_dbname,
                'RedshiftUser': redshift.get_cluster_user,
                'RedshiftIamRole': redshift.get_cluster_iam_role,
                'ScriptS3Path': redshift_bootstrap_script_s3_path,
                'LambdaArn': lambda_run_redshift_script.function_arn}
        )


def get_md5(account: str, region: str, script_s3_path: str, length: int = 8) -> str:
    md5 = hashlib.new('md5')
    md5.update(account.encode('utf-8'))
    md5.update(region.encode('utf-8'))
    md5.update(script_s3_path.encode('utf-8'))
    return md5.hexdigest()[:length]
