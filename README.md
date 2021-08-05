
# AWS Redshift Infrastructure Automation

As analytics solutions have moved away from the one-size-fits-all model to choosing the right tool for the right function, architectures have become more optimized and performant while simultaneously becoming more complex. Solutions leveraging Amazon Redshift will often be used alongside services including AWS DMS, AWS AppSync, AWS Glue, AWS SCT, Amazon Sagemaker, Amazon QuickSight, and more. One of the core challenges of building these solutions can oftentimes be the integration of these services.

This solution takes advantage of the repeated integrations between different services in common use cases, and leverages the [AWS CDK](https://aws.amazon.com/cdk/) to automate the provisioning of AWS analytics services, primarily Amazon Redshift. Deployment is now customizing a JSON configuration file indicating the resources to be used, and this solution takes those inputs to auto-provision the required infrastructure dynamically.

PLEASE NOTE: This solution is meant for proof of concept or demo use cases, and not for production workloads.

## Table of Contents

1. [Overview of Deployment](#overview-of-deployment)
1. [Prerequisites](#prerequisites)
	1. [Launching a VPC](#launching-a-vpc)
	1. [Auto-assigning public IPv4 addresses](#auto-assigning-public-ipv4-addresses)
1. [Deployment Steps](#deployment-steps)
	1. [Configure the config file](#configure-the-config-file)
	1. [Launch the staging template](#launch-the-staging-template)
1. [Troubleshooting](#troubleshooting)

## Overview of Deployment

This project consists of a two-phase deployment: the staging infrastructure, and the target infrastructure. The target infrastructure is the end-goal configuration of AWS analytics services which are needed for a POC or other use case. The staging infrastructure will launch an EC2 instance to run a CDK application which will provision the resources of this target infrastructure. 

To achieve this, a JSON-formatted config file specifying the desired service configurations needs to be uploaded to an S3 bucket. The location of this file in S3 is used as a parameter in the CloudFormation stack, alongside further details of the staging infrastructure. Once the CloudFormation stack is launched, the resources are provisioned automatically.

Here you can see a diagram giving an overview of this flow:

![Architecture Flow](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/images/Architecture_Flow.png)

The following sections give further details of how to complete these steps.

## Prerequisites

In order to run the staging stack, some resources need to be preconfigured:
* A VPC containing a public subnet that has IPv4 auto-assign enabled -- if either of these aren't configured please see [launching a VPC](#launching-a-vpc) and [auto-assigning public IPv4 addresses](#auto-assigning-public-ipv4-addresses) below
* A key pair that can be accessed (see [the documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html#having-ec2-create-your-key-pair) on how to create a new one)
* If using DMS or SCT, opening source firewalls/ security groups to allow for traffic from AWS

If these are complete, continue to [deployment steps](#deployment-steps).

### Launching a VPC

An option for provisioning the VPC is to use the [VPC Launch Wizard console](https://console.aws.amazon.com/vpc/#wizardSelector:) -- you can see the details of the infrastructure launched using this wizard [here](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Scenario1.html).
1. Open the VPC Launch Wizard console linked above and press **Select** for creating a VPC with a single public subnet 
2. Configure your desired VPC size, VPC name, subnet size, and subnet name -- other values can be kept as default
3. Press **Create VPC**

These resources will be sufficient for the staging infrastructure. If a manually provisioned VPC is preferred, having at minimum a public subnet is required.

### Auto-assigning public IPv4 addresses

To ensure instances launched in this subnet will be auto-assigned public IPv4 addresses, 
1. Navigate to the **Subnets** tab in the VPC console -- select the subnet you intend to use for your staging infrastructure (i.e. the subnet name created with the launch wizard above), and under details, see whether the "Auto-assign public IPv4 address" value is Yes or No

	![Autoassign](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/images/Austoassign-step1.png)

2. If the value is No, select **Actions** > **Modify auto-assign IP settings**

	![Modify](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/images/Autoassign-step2.png)

	select the "Enable auto-assign public IPv4 address" checkbox

	![Checkbox](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/images/Autoassign-step3.png)
	
3. Press **Save**


## Deployment Steps

In order to launch the staging and target infrastructures, download the [user-config-template.json](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/user-config-template.json) file and the [CDKstaging.yaml](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/CDKstaging.yaml) file in this repo. 

### Configure the config file

The structure of the config file has two parts: (1) a list of key-value pairs, which create a mapping between a specific service and whether it should be launched in the target infrastructure, and (2) configurations for the service that are launched in the target infrastructure. Open the [user-config-template.json](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/user-config-template.json) file and replace the values for the Service Keys in the first section with the appropriate  Launch Value defined in the table below. If you're looking to create a resource, define the corresponding Configuration fields in the second section.


| Service Key | Launch Values | Configuration | Description |
| ----------- | ------------- | ------------- | ----------- |
| `vpc_id`    | `CREATE`, existing VPC ID | In case of `CREATE`, configure `vpc`:<br>`on_prem_cidr`: CIDR block used to connect to VPC (for security groups)<br>`vpc_cidr`: The CIDR block used for the VPC private IPs and size<br>`number_of_az`: Number of Availability Zones the VPC should cover<br>`cidr_mask`: The size of the public and private subnet to be launched in the VPC. | [REQUIRED] The VPC to launch the target resources in -- can either be an existing VPC or created from scratch. |
| `redshift_endpoint` | `CREATE`, `N/A` | In case of `CREATE`, configure `redshift`:<br>`cluster_identifier`: Name to be used in the cluster ID<br>`database_name`: Name of the database<br>`node_type`: `ds2.xlarge`, `ds2.8xlarge`, `dc1.large`, `dc1.8xlarge`, `dc2.large`, `dc2.8xlarge`, `ra3.xlplus`, `ra3.4xlplus`, or `ra3.16xlarge`<br>`number_of_nodes`: Number of compute nodes<br>`master_user_name`: Username to be used for Redshift database<br>`subnet_type`: Subnet type the cluster should be launched in -- `PUBLIC` or `PRIVATE` (note: must be existing in VPC) | Launching a Redshift cluster. |
| `dms_instance_private_endpoint` | `CREATE`, `N/A` | Requires at least one public subnet in VPC. | The DMS instance used to migrate data. |
| `dms_on_prem_to_redshift_target` | `CREATE`, `N/A` | *Can only CREATE if are also creating DMS instance and Redshift cluster.*<br>In case of `CREATE`, configure `dms_on_prem_to_redshift`:<br>`source_db`: Name of source database to migrate<br>`source_engine`: Engine type of the source<br>`source_schema`: Name of source schema to migrate<br>`source_host`: DNS endpoint of the source<br>`source_user`: Username of the database to migrate<br>`source_port`: [INT] Port to connect to connect on<br>`migration_type`: `full-load`, `cdc`, or `full-load-and-cdc` | Creates a migration task and migration endpoints between a source and Redshift configured above. |
| `sct_on_prem_to_redshift_target` | `CREATE`, `N/A` | *Can only CREATE if are also creating Redshift cluster.*<br>In case of `CREATE`, uses configuration from `dms_on_prem_to_redshift` (see above) and `sct_on_prem_to_redshift`:<br>`key_name`: EC2 key pair name to be used for EC2 running SCT<br>`s3_bucket_output`: S3 bucket to be used for SCT artifacts | Launches an EC2 instance and installs SCT to be used for schema conversion. |


You can see an example of a completed config file under [user-config-sample.json](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/user-config-sample.json).

Once all appropriate Launch Values and Configurations have been defined, upload the config file to an S3 bucket.

### Launch the staging template

1. Open the [CloudFormation console](https://console.aws.amazon.com/cloudformation/) and under **Create stack** select **With new resources (standard)**
2. Select **Upload a template file** under **Specify template** and choose the downloaded [CDKstaging.yaml](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/CDKstaging.yaml) file, then press **Next**
3. Fill in the fields with the following values:
	| Field Name | Value |
	| ---------- | ----- |
	| Stack name | A name to be used for the launched CloudFormation stacks |
	| Configuration File | The URI of the config file uploaded to S3 in the previous section |
	| EC2 AMI | The AMI to be used for the staging instance -- do not change unless need to for compliance requirements |
	| Key Pair | Select the key pair in your account to be used to SSH into the staging instance |
	| On Prem CIDR | The CIDR to be used to SSH into the staging instance |
	| Subnet ID | Select the public subnet with IPv4 auto-assign enabled from the prerequisites |
	| Source Password | Password of the source database |
	
	An example:

	![Example](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/blob/main/images/CloudFormationTemplate.png)

	Press **Next**
4. To make troubleshooting easier, under **Stack creation options**, select Disabled under "Rollback on failure" -- press **Next**
5. At the bottom of the page, select the IAM acknowledgment and press **Create stack** to launch the stack

At this point the launch will be initiated. Please see troubleshooting below if the stack launch stalls at any point.

## Troubleshooting

In the case that the template stall, logs of CloudFormation/CDK events and errors will be generated in the staging EC2 instance. This can be accessed by connecting to the instance.

1. Navigate to the [EC2 console](https://console.aws.amazon.com/ec2/v2/) and select the checkbox next to the EC2 instance named "[your CloudFormation stack name]-EC2Instance"
2. In the top right corner, press **Connect**
3. Choose the tab corresponding to the preferred connection option and follow the instructions

	1. In the case that you choose to connect using the browser-based EC2 Instance Connect console, update the EC2 instance security group to allow for traffic from the source CIDR for [AWS IP address ranges](https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html#filter-json-file) associated to EC2 in the region you are using:
		
		Mac: `$ curl -s https://ip-ranges.amazonaws.com/ip-ranges.json| jq -r '.prefixes[] | select(.region=="us-east-1") | select(.service=="EC2_INSTANCE_CONNECT") | .ip_prefix'`
		
		Windows: `PS C:\> Get-AWSPublicIpAddressRange -Region us-east-1 -ServiceKey EC2_INSTANCE_CONNECT | select IpPrefix`
		
		Replace "us-east-1" with the region you intend on using.
	
4. Run `sudo tail -35f /var/log/cloud-init-output.log` to access the logs

## Feedback

Our aim is to make this tool as dynamic and comprehensive as possible, so we’d love to hear your feedback. Let us know your experience deploying the solution, and share any other use cases that the automation solution doesn’t yet support. Please use the [Issues](https://github.com/aws-samples/amazon-redshift-infrastructure-automation/issues) tab under this repo, and we’ll use that to guide our roadmap. 

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

