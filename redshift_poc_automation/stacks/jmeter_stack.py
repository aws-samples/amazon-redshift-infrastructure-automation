from aws_cdk import aws_iam
from aws_cdk import aws_ec2
from aws_cdk import core
from aws_cdk import aws_secretsmanager
import boto3
import json


class JmeterStack(core.Stack):

    def __init__(
            self,
            scope: core.Construct, id: str,
            cluster,
            other_config: dict,
            redshift_config: dict,
            vpc,
            stack_log_level: str,
            onprem_cidr: str,
            **kwargs

    ) -> None:
        super().__init__(scope, id, **kwargs)

        keyname = other_config.get('key_name')
        jmeter_node_type = other_config.get('jmeter_node_type')
        redshift_host = cluster.get_cluster_host
        redshift_db = cluster.get_cluster_dbname
        redshift_user = cluster.get_cluster_user
        redshift_port = cluster.get_cluster_iam_role
        secret_arn = 'RedshiftClusterSecretAA'
        amiID = 'ami-042e0580ee1b9e2af'

        account_id = boto3.client('sts').get_caller_identity().get('Account')

        with open("./jmeterconfig.sh") as f:
            user_data = f.read()

        with open("./jmeterconfig_2.sh") as f_2:
            user_data_2 = f_2.read()

        # Instance Role and SSM Managed Policy

        role_policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::" + account_id + ":root"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        client = boto3.client('iam')
        roles = client.list_roles()
        Role_list = roles['Roles']
        for key in Role_list:
            name = key['RoleName']
            if name == 'window-cli-role':
                windowcliexists = 1
            else:
                windowcliexists = 0

        #adminrole = aws_iam.Role(
        #  self,
        #  id='windows-cli-role',
        #  assumed_by=aws_iam.ArnPrincipal("arn:aws:iam::" + account_id + ":root"),
        #  role_name='windows-cli-role'
        #)
        #adminrole.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))

        #role = aws_iam.Role(self, "WindowsCLIrole", assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com"))

        #role.add_to_policy(aws_iam.PolicyStatement(
        #    actions=["sts:AssumeRole"],
        #    resources=["arn:aws:iam::" + account_id + ":role/windows-cli-role"],
        #    effect=aws_iam.Effect.ALLOW
        #))
        #role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonEC2RoleforSSM"))
        #role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite"))

        # secrets_client = boto3.client(service_name='secretsmanager', region_name='us-east-1')
        # get_secret_value_response = secrets_client.get_secret_value(
        #    SecretId=secret_arn
        # )
        # redshift_pwd = [value for value in get_secret_value_response.values()][3]

        ### TAKE THIS OUT SO THAT INSTANCE IS NOT PUBLIC ###
        subnet = aws_ec2.SubnetSelection(subnet_type=aws_ec2.SubnetType('PUBLIC'))

        # my_security_group = aws_ec2.SecurityGroup(self, "SecurityGroup",
        #                                       vpc=vpc.vpc,
        #                                       description="Allow ssh access to ec2 instances",
        #                                       allow_all_outbound=True
        #                                       )
        # my_security_group.add_ingress_rule(aws_ec2.Peer.ipv4('10.200.0.0/24'), aws_ec2.Port.tcp(22), "allow ssh access from the world")
        # my_security_group.add_ingress_rule(my_security_group, aws_ec2.Port.all_tcp(), "self-referencing rule")
        my_security_group = vpc.get_vpc_security_group

        my_security_group.add_ingress_rule(peer=aws_ec2.Peer.ipv4(onprem_cidr), connection=aws_ec2.Port.tcp(3389),
                                           description="RDP from anywhere")

        custom_ami = aws_ec2.WindowsImage(aws_ec2.WindowsVersion.WINDOWS_SERVER_2019_ENGLISH_FULL_BASE);
        # Instance
        firstcommand = "\naws configure set role_arn arn:aws:iam::" + account_id + ":role/windows-cli-role\n"
        input_data = user_data + firstcommand + user_data_2
        instance = aws_ec2.Instance(self, "Instance",
                                    instance_type=aws_ec2.InstanceType(jmeter_node_type),
                                    machine_image=custom_ami,
                                    vpc=vpc.vpc,
                                    vpc_subnets=subnet,
                                    key_name=keyname,
                                    #role=role,
                                    security_group=my_security_group,
                                    #            resource_signal_timeout=core.Duration.minutes(5),
                                    user_data=aws_ec2.UserData.custom(input_data)
                                    )
