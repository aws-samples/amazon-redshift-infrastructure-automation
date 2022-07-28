# AWS Analytics Automation Toolkit Permission List

**CloudFormation Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "cloudformation:ListStacks",
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "cloudformation:DescribeStackEvents",
                "cloudformation:DeleteStack",
                "cloudformation:CreateChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:DescribeStacks"
            ],
            "Resource": [
                "arn:aws:cloudformation::<YOUR ACCOUNT NUMBER>:stack/*-sct-stack/*",
                "arn:aws:cloudformation::<YOUR ACCOUNT NUMBER>:stack/*-dms-stack/*",
                "arn:aws:cloudformation::<YOUR ACCOUNT NUMBER>:stack/*-redshift-stack/*",
                "arn:aws:cloudformation::<YOUR ACCOUNT NUMBER>:stack/*-vpc-stack/*",
                "arn:aws:cloudformation::<YOUR ACCOUNT NUMBER>:stack/CDKToolkit/*"
            ]
        }
    ]
}
```

**CloudShell Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "cloudshell:GetEnvironmentStatus",
                "cloudshell:StartEnvironment",
                "cloudshell:CreateSession",
                "cloudshell:GetFileUploadUrls",
                "cloudshell:PutCredentials"
            ],
            "Resource": "arn:aws:cloudshell::<YOUR ACCOUNT NUMBER>:environment/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "cloudshell:CreateEnvironment",
            "Resource": "*"
        }
    ]
}
```

**DMS Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "dms:CreateReplicationTask",
            "Resource": [
                "arn:aws:dms::<YOUR ACCOUNT NUMBER>:endpoint:*",
                "arn:aws:dms::<YOUR ACCOUNT NUMBER>:rep:*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "dms:CreateReplicationSubnetGroup",
                "dms:DescribeReplicationInstances",
                "dms:CreateEndpoint",
                "dms:DescribeEndpoints",
                "dms:DescribeReplicationSubnetGroups",
                "dms:DescribeReplicationTasks",
                "dms:CreateReplicationInstance"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "dms:DeleteReplicationTask",
                "dms:DeleteReplicationSubnetGroup",
                "dms:DeleteEndpoint",
                "dms:DeleteReplicationInstance"
            ],
            "Resource": [
                "arn:aws:dms::<YOUR ACCOUNT NUMBER>:endpoint:*",
                "arn:aws:dms::<YOUR ACCOUNT NUMBER>:rep:*",
                "arn:aws:dms::<YOUR ACCOUNT NUMBER>:task:*",
                "arn:aws:dms::<YOUR ACCOUNT NUMBER>:subgrp:*"
            ]
        }
    ]
}
```

**Health Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "health:DescribeEventAggregates",
            "Resource": "*"
        }
    ]
}
```

**IAM Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "iam:SimulatePrincipalPolicy",
                "iam:GetRole",
                "iam:PassRole",
                "iam:DetachRolePolicy",
                "iam:DeleteRolePolicy",
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy"
            ],
            "Resource": [
                "arn:aws:iam::<YOUR ACCOUNT NUMBER>:role/dms-cloudwatch-logs-role",
                "arn:aws:iam::<YOUR ACCOUNT NUMBER>:role/dms-vpc-role",
                "arn:aws:iam::<YOUR ACCOUNT NUMBER>:role/dms-access-for-endpoint",
                "arn:aws:iam::<YOUR ACCOUNT NUMBER>:role/*-redshift-stack-redshiftClusterRole*",
                "arn:aws:iam::<YOUR ACCOUNT NUMBER>:role/*-sct-stack-WindowsCLIrole*",
                "arn:aws:iam::<YOUR ACCOUNT NUMBER>:role/windows-cli-role"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "iam:CreateInstanceProfile",
                "iam:DeleteInstanceProfile",
                "iam:RemoveRoleFromInstanceProfile",
                "iam:AddRoleToInstanceProfile"
            ],
            "Resource": "arn:aws:iam::<YOUR ACCOUNT NUMBER>:instance-profile/*-sct-stack-InstanceInstanceProfile*"
        }
    ]
}
```

**Redshift Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "redshift:CreateClusterSubnetGroup",
            "Resource": "arn:aws:redshift:*:<YOUR ACCOUNT NUMBER>:subnetgroup:*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "redshift:DeleteClusterSubnetGroup",
            "Resource": "arn:aws:redshift:*:<YOUR ACCOUNT NUMBER>:subnetgroup:*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "redshift:CreateCluster",
            "Resource": "arn:aws:redshift:*:<YOUR ACCOUNT NUMBER>:cluster:*"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": "redshift:DescribeClusters",
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": "redshift:DescribeLoggingStatus",
            "Resource": "arn:aws:redshift:*:<YOUR ACCOUNT NUMBER>:cluster:*"
        },
        {
            "Sid": "VisualEditor5",
            "Effect": "Allow",
            "Action": "redshift:ModifyClusterIamRoles",
            "Resource": "arn:aws:redshift:*:<YOUR ACCOUNT NUMBER>:cluster:targetcluster-*"
        },
        {
            "Sid": "VisualEditor6",
            "Effect": "Allow",
            "Action": "redshift:DeleteCluster",
            "Resource": "arn:aws:redshift:*:<YOUR ACCOUNT NUMBER>:cluster:*"
        }
    ]
}
```

**Secrets Manager Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetSecretValue",
                "secretsmanager:CreateSecret",
                "secretsmanager:DeleteSecret"
            ],
            "Resource": [
                "arn:aws:secretsmanager::<YOUR ACCOUNT NUMBER>:secret:*-SourceDBPassword-*",
                "arn:aws:secretsmanager::<YOUR ACCOUNT NUMBER>:secret:*-RedshiftPassword-*",
                "arn:aws:secretsmanager::<YOUR ACCOUNT NUMBER>:secret:*-RedshiftClusterSecretAA-*"
            ]
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "secretsmanager:GetRandomPassword",
                "secretsmanager:ListSecrets"
            ],
            "Resource": "*"
        }
    ]
}
```

**SSM Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ssm:GetParametersByPath",
                "ssm:GetParameters",
                "ssm:GetParameter"
            ],
            "Resource": "arn:aws:ssm:us-east-1:*:parameter/*"
        }
    ]
}
```

**STS Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "sts:GetCallerIdentity",
            "Resource": "*"
        }
    ]
}
```

**VPC Permissions**

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ec2:CreateVpc",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeImages",
                "ec2:DescribeInternetGateways",
                "ec2:DescribeAddresses",
                "ec2:DescribeInstances",
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeVpcs",
                "ec2:DescribeNatGateways",
                "ec2:DescribeSubnets",
                "ec2:DescribeRouteTables",
                "ec2:DescribeVpnGateways",
                "ec2:DescribeSecurityGroups"
            ],
            "Resource": "*"
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": "ec2:CreateInternetGateway",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:internet-gateway/*"
        },
        {
            "Sid": "VisualEditor3",
            "Effect": "Allow",
            "Action": "ec2:AllocateAddress",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:elastic-ip/*"
        },
        {
            "Sid": "VisualEditor4",
            "Effect": "Allow",
            "Action": "ec2:CreateTags",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:route-table/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:internet-gateway/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:elastic-ip/*"
            ]
        },
        {
            "Sid": "VisualEditor5",
            "Effect": "Allow",
            "Action": "ec2:ModifyVpcAttribute",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*"
        },
        {
            "Sid": "VisualEditor6",
            "Effect": "Allow",
            "Action": "ec2:CreateRouteTable",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:route-table/*"
            ]
        },
        {
            "Sid": "VisualEditor7",
            "Effect": "Allow",
            "Action": "ec2:CreateSubnet",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*"
            ]
        },
        {
            "Sid": "VisualEditor8",
            "Effect": "Allow",
            "Action": "ec2:AttachInternetGateway",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:internet-gateway/*"
            ]
        },
        {
            "Sid": "VisualEditor9",
            "Effect": "Allow",
            "Action": "ec2:CreateSecurityGroup",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*"
            ]
        },
        {
            "Sid": "VisualEditor10",
            "Effect": "Allow",
            "Action": "ec2:RevokeSecurityGroupEgress",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*"
        },
        {
            "Sid": "VisualEditor11",
            "Effect": "Allow",
            "Action": "ec2:AuthorizeSecurityGroupEgress",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*"
        },
        {
            "Sid": "VisualEditor12",
            "Effect": "Allow",
            "Action": [
                "ec2:ReleaseAddress",
                "ec2:DeleteSubnet",
                "ec2:DeleteSecurityGroup",
                "ec2:DeleteRoute",
                "ec2:DeleteNatGateway",
                "ec2:DeleteInternetGateway",
                "ec2:DetachInternetGateway",
                "ec2:DeleteVpc",
                "ec2:DisassociateRouteTable",
                "ec2:DeleteRouteTable"
            ],
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpc/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:natgateway/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:route-table/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:internet-gateway/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:elastic-ip/*"
            ]
        },
        {
            "Sid": "VisualEditor13",
            "Effect": "Allow",
            "Action": "ec2:AuthorizeSecurityGroupIngress",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*"
        },
        {
            "Sid": "VisualEditor14",
            "Effect": "Allow",
            "Action": "ec2:ModifySubnetAttribute",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*"
        },
        {
            "Sid": "VisualEditor15",
            "Effect": "Allow",
            "Action": "ec2:RevokeSecurityGroupIngress",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*"
        },
        {
            "Sid": "VisualEditor16",
            "Effect": "Allow",
            "Action": "ec2:CreateRoute",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:route-table/*"
        },
        {
            "Sid": "VisualEditor17",
            "Effect": "Allow",
            "Action": "ec2:AssociateRouteTable",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:route-table/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:vpn-gateway/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:internet-gateway/*"
            ]
        },
        {
            "Sid": "VisualEditor18",
            "Effect": "Allow",
            "Action": "ec2:CreateNatGateway",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:natgateway/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:elastic-ip/*"
            ]
        },
        {
            "Sid": "VisualEditor19",
            "Effect": "Allow",
            "Action": "ec2:RunInstances",
            "Resource": [
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:security-group/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:instance/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:subnet/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:key-pair/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:volume/*",
                "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:network-interface/*",
                "arn:aws:ec2:*::image/*"
            ]
        },
        {
            "Sid": "VisualEditor20",
            "Effect": "Allow",
            "Action": "ec2:TerminateInstances",
            "Resource": "arn:aws:ec2:*:<YOUR ACCOUNT NUMBER>:instance/*"
        }
    ]
}
```
