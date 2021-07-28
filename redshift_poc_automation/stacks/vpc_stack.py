from aws_cdk import aws_ec2
from aws_cdk import core
import random
import string


class GlobalArgs():
    """
    Helper to define global statics
    """

    OWNER = "Redshift POC SSA team"
    ENVIRONMENT = "development"
    REPO_NAME = "redshift-demo"
    VERSION = "2021_03_15"

class VpcStack(core.Stack):

    def __init__(
        self,
        scope: core.Construct,
        id: str,
        stack_log_level: str,
        vpc_id: str,
        vpc_config: dict,

        ** kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        if vpc_id != "CREATE":
            self.vpc = aws_ec2.Vpc.from_lookup(
                self, "vpc",
                vpc_id=vpc_id
            )
        else:
            vpc_cidr = vpc_config.get('vpc_cidr')
            cidr_mask = int(vpc_config.get('cidr_mask'))
            number_of_az = int(vpc_config.get('number_of_az'))

            self.vpc = aws_ec2.Vpc(
                self,
                "RedshiftPOCVpc",
                cidr= vpc_cidr,
                max_azs=number_of_az,
                enable_dns_support=True,
                enable_dns_hostnames=True,
                subnet_configuration=[
                    aws_ec2.SubnetConfiguration(
                        name="public_subnet", cidr_mask=cidr_mask, subnet_type=aws_ec2.SubnetType.PUBLIC
                    ),
                    aws_ec2.SubnetConfiguration(
                        name="private_subnet", cidr_mask=cidr_mask, subnet_type=aws_ec2.SubnetType.PRIVATE
                    )
                ]
            )

        letters = string.ascii_lowercase
        tail = ''.join(random.choice(letters) for i in range(5))

        self.dms_security_group = aws_ec2.SecurityGroup(
             self,
             id = "sct-sg-dms-" + tail,
             vpc = self.vpc,
             security_group_name = "sct-sg-dms" + tail,
             description = "Gives DMS instance access to Redshift"
        )
        self.dms_security_group.add_ingress_rule(peer=self.dms_security_group, connection=aws_ec2.Port.all_traffic(), description="Self-referencing rule.")
        self.dms_security_group.add_ingress_rule(peer=aws_ec2.Peer.any_ipv4(), connection=aws_ec2.Port.tcp(22), description="SSH from anywhere")


        output_1 = core.CfnOutput(
            self,
            "New SG",
            value=f"{self.dms_security_group.security_group_id}",
            description="New security group of this VPC."
        )

    # properties to share with other stacks
    @property
    def get_vpc(self):
        return self.vpc

    @property
    def get_vpc_public_subnet_ids(self):
        return self.vpc.select_subnets(
            subnet_type=aws_ec2.SubnetType.PUBLIC
        ).subnet_ids

    @property
    def get_vpc_private_isolated_subnet_ids(self):
        return self.vpc.select_subnets(
            subnet_type=aws_ec2.SubnetType.ISOLATED
        ).subnet_ids

    @property
    def get_vpc_private_subnet_ids(self):
        return self.vpc.select_subnets(
            subnet_type=aws_ec2.SubnetType.PRIVATE
        ).subnet_ids

    @property
    def get_vpc_security_group_id(self):
        return self.dms_security_group.security_group_id

    @property
    def get_vpc_security_group(self):
        return self.dms_security_group
