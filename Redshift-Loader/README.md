# Redshift Auto Loader 

With this Redshift Auto loader framework now you can simply drop your files in S3 bucket and let this framework 
automatically create tables for your files and continuously load teh files into your Amazon Redshift data warehouse.  This framework has two functional processes in it 
* Auto schema detection and creating tables in Redshift Cluster
* Continuous loading of the files from your S3 Bucket. As files are dropped in S3 bucket schema detection and data loading processes are triggered. No scheduling is required. 

This process uses Redshift [copy command](https://docs.aws.amazon.com/redshift/latest/dg/t_Loading_tables_with_the_COPY_command.html) to load data into data warehouse. 

Please read through below steps to understand the architecture and how to deploy and run the process.

## Table of Contents

[Architecture](#architecture)

- [Process Flow](#process-flow)

- [Components](#components)

[Cost](#cost)

[Pre Requirements](#pre-requirements)

[CloudFormation Template](#cloudFormation-template)

- [Permissions required for CF](#permissions-required-for-cf)

- [CloudFormation Parameters](#cloudFormation-parameters)

- [Installation](#installation)

- [CloudFormation Output Tabs](#cloudFormation-output-tabs)

[Naming Standards](#setting-up-s3-buckets)

- [Table Names](#table-names)
- [S3 Prefixes](#prefixes)

[Security](#security)

- [Lambda Execution Role](#lambda-execution-role)

[Notifications](#notifications)


[Operations](#operations)

- [Loading Your First File](#loading-your-first-file)

- [Controlling Copy command parameters](#controlling-copy-command-parameters)

- [Deleting or reloading files](#deleting-or-reloading-files)

- [Viewing Previous loads](#viewing-vrevious-loads)
- [Viewing Current Loads](#viewing-current-Loads)
- [Viewing Schedules in Event Bridge](#viewing-vchedules-in-vvent-bridge)
- [Reviewing Logs](#reviewing-logs)
- [Pause and Resume the process](pause-and-resume-the-process)
- [Deleting the Framework](#deleting-the-framework)

## Architecture 
This process built using serverless components which means zero administration for you. 

Below is high level Process Flow Diagram ![data flow diagram](/Redshift-Loader/Images/redshift_loader.png)

### Process Flow

Cloudformation needs an S3 bucket name and will create a directory **s3-to-redshift-loader-utility**. This acts as the data repository and all sub directories in the bucket (first level) are considered as Tables. Each entity/table can contain the files or sub directory. Following steps explain the process in detail

0.  User place  a file is in **s3-to-redshift-loader-utility** directory 
1.  Process defines a file based trigger and as soon a file is placed in the **s3-to-redshift-loader-utility** directory an S3 event notification trigger is kicked off.
2.  S3 event notification will call an AWS Lambda function **s3LoaderUtilLogFileMetadata** 
3.  * a. AWS Lambda function **s3LoaderUtilLogFileMetadata** logs the file metadata and the table level configurations into Amazon DynamoDB tables e.g. **s3_data_loader_file_metadata** and **s3_data_loader_table_config**
    * b. AWS Lambda function s3LoaderUtilLogFileMetadata detects schema for the given file, creates the respective table in Amazon Redshift.
4.  An AWS eventbridge **KickoffFileProcessingSchedule** is scheduled by default to run every 5 mins and will trigger a call to AWS lambda function **s3LoaderUtilKickoffFileProcessing**
5.  **s3LoaderUtilKickoffFileProcessing** refers to the metadata stored in Amazon DynamoDB table **s3_data_loader_table_config** and for any table with **"load_status= active"** it will call AWS lambda function **s3LoaderUtilProcessPendingFiles**, this call can run the lambda function in parallel.
6.  * a. AWS Lambda function **s3LoaderUtilProcessPendingFiles** is invoked for each table and it would pick up all the files from the Amazon Dynamo DB table "s3_data_loader_file_metadata" where the **s3_data_loader_file_metadata.file_created_timestamp** is greater then the **s3_data_loader_table_config.max_file_proccessed_timestamp**
    * b. **s3LoaderUtilProcessPendingFiles** prepares a COPY Command SQL using the **s3_data_loader_table_config** and push the copy command SQL into an AWS SQS FIFO Queue **S3LoaderSQSQueue**
7.  * a. An AWS eventbridge rule **QueueRSProcessingSchedule** is scheduled by default to run every 5 mins and will trigger a call to AWS lambda function **s3LoaderUtilProcessQueueLoadRS**
    * b. AWS lambda function **s3LoaderUtilProcessQueueLoadRS** polls the AWS SQS queue **S3LoaderSQSQueue**
8.  * a. AWS lambda function **s3LoaderUtilProcessQueueLoadRS** execute the Copy commands using Amazon Redshift data api asynchronously and logs the informtion into the Amazon DynamoDB table **s3_data_loader_log**.  More than one copy command can run in parallel, which means more than one table can be loaded. 
    * b. Amazon Redshift data api loads the data to Amazon Redshift 
9.  * a. Amazon Redshift data api trigger the AWS eventbridge once the data api query execution is complete
    * b. AWS eventbridge **UpdateLogTableEventBased** invoke the AWS lambda **s3LoaderUtilUpdateLogTable** 
10. AWS lambda **s3LoaderUtilUpdateLogTable** update the log entry for the copy command in the Amazon DynamoDB table **s3_data_loader_log** with final status e.g. Finished or Aborted etc.



### Components 

Following AWS Services are created and used by this framework
#### [AWS Lambda](https://aws.amazon.com/lambda/) 
* CustomResourceLambdaFunction
* s3LoaderUtilKickoffFileProcessing
* s3LoaderUtilLogFileMetadata
* s3LoaderUtilProcessPendingFiles
* s3LoaderUtilProcessQueueLoadRS
* s3LoaderUtilUpdateLogTable

#### [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) 
* s3_data_loader_log
* s3_data_loader_table_config
* s3_data_loader_file_metadata

#### [Amazon SQS](https://aws.amazon.com/sqs/) 
* S3LoaderSQSQueue

#### [AWS EventBridge](https://aws.amazon.com/eventbridge/)  
* KickoffFileProcessingSchedule
* QueueRSProcessingSchedule
* UpdateLogTableEventBased

#### [AWS S3 Event Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html) 
* s3LoaderUtilLogFileMetadataLambdaTrigger

#### [IAM Roles and Permissions](https://aws.amazon.com/iam/)
* s3LoaderLambdaRole
* s3LoaderUtilLogFileMetadataInvokePermission

### Cost

This architecture uses serverless services, most of these services have free tier available. You can learn more about AWS Free Tier [here](https://aws.amazon.com/free/?all-free-tier.sort-by=item.additionalFields.SortRank&all-free-tier.sort-order=asc&awsf.Free%20Tier%20Types=*all&awsf.Free%20Tier%20Categories=*all).

**NOTE:** If your workload goes above and beyond free tier threshold and you would like to understand the pricing then please follow below links

[AWS Lambda](https://aws.amazon.com/lambda/pricing/)
[Amazon DynamoDB](https://aws.amazon.com/dynamodb/pricing/)
[Amazon SQS](https://aws.amazon.com/sqs/pricing/)
[Amazon EventBridge](https://aws.amazon.com/eventbridge/pricing/)

### Pre Requirements

This framework does not create 
* S3 bucket 
* Amazon Redshift Cluster 
* Amazon Redshift Cluster IAM Role
* Amazon Redshift Tables are deployed with matching schema with files on Amazon S3 

It is expected that you already have S3 bucket and Amazon Redshift pre created for you. If not please follow these instructions here for [S3 Bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/creating-bucket.html) and here for [Amazon Redshift](https://docs.aws.amazon.com/redshift/latest/gsg/rs-gsg-launch-sample-cluster.html) and here for Amazon [Redshift Cluster IAM Role](https://docs.aws.amazon.com/redshift/latest/dg/c-getting-started-using-spectrum-create-role.html)

### CloudFormation Template
Below section talks about CloudFormation which when run creates infrastructure that you need to run this framework

#### CloudFormation Parameters 

Following parameters have to be set for successful creation of resources.  Make sure you have collected these values beforehand. 

|Parameter Name	| Default value |	Description |
|:--------------|:--------------|:--------------|
|CopyCommandSchedule|	cron(0/5 * ? * * *)	| "Below Event Bridge rules are triggered based on this schedule- KickoffFileProcessingSchedule & QueueRSProcessingSchedule Default is 5 minute."|
|DatabaseName|	dev|	Redshift Database name.| 
|DatabaseSchemaName|	public	|Redshift Schema name|
|DatabaseUserName|	demo|	Redshift user name who has access to run copy commands on redshift db/schema. |
|RedshiftClusterIdentifier|	democluster|	Redshift Cluster Name|
|RedshiftServerlessWorkgroup|N/A|	Redshift wwrkgroup Name, if you plan to use provisioned cluster keep this value to default e.g. N/A|
|RedshiftIAMRoleARN	|arn:aws:iam::7000000000:role/RedshiftDemoRole|	Redshift Cluster attached role which has access to s3 bucket. This role is used in Copy commands|
|SourceS3Bucket	|Your-bucket-name	|S3 bucket where data is located|
|CopyCommandOptions	|delimiter '\|' gzip|Provide the additional COPY command data format parameters|


#### Installation 

This repository includes a CloudFormation template [RedshiftAutoLoader.yaml](https://redshift-demos.s3.amazonaws.com/redshift-loader/redshift-s3-data-autoloader.yaml) which will create much of what is needed to set up the Auto Loader. This section details the setup and use of the template.

This is a visual architecture of the CloudFormation installer:


 
Click on below **Launch Button** to launch the Cloud Formation:

[<img src="https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png" target=\”_blank\”>](https://console.aws.amazon.com/cloudformation/home?#/stacks/new?stackName=RedshiftLoader&templateURL=https://redshift-demos.s3.amazonaws.com/redshift-loader/redshift-s3-data-autoloader.yaml
)

#### Additional Configuration for Redshift Serverless

Once cloud formation is succesful , go to the **output** tab and note the IAM role name. Auto loader uses IAM authentication when connecting to Redshift serverless and a user with IAMR:<lambda_iam_role_name> is created in Redshift serverless. 

![CFN output](/Redshift-Loader/Images/cfn_lambda_role.png)


- Login to Amazon Redshift Serverless as a SUPER User and run the following GRANT 
   
   **grant create on database <db_name> to "IAMR:<lamda_iam_role_name>";**

**Notes**

- This stack will be created in the same region where you invoke the template.
- The input parameters are not cross-checked at template creation time, so make sure that they are correct
- The stack creates the Lambda functions, Lambda trigger as well as the execution role - so they will be managed as part of the stack. 
- For Redshift serverless IAMR:<lambda_iam_role_name> should have the database privillages on the schema and tables used for auto loader


#### CloudFormation Output Tabs

### Naming Standards
- #### Table Names
- #### S3 Prefixes
### Security

- #### Lambda Execution Role

### Notifications

S3 loader utility will not generate any notification on failure of the redshift data load. For monitoring the data laod current or past refer to the    section **Viewing Previous loads** and **Viewing Current loads** below. we plan to include the email based notification in next release. 

### Operations

- #### Loading Your First File
    To load your first file follow the steps
    1. Create a new directoy under **s3-to-redshift-loader-utility** e.g. **test_tbl**
    2. Upload a file to the newly created directory e.g. **s3-to-redshift-loader-utility\test_tbl**
    3. (optional) create any sub directory to store data into partition e.g. **s3-to-redshift-loader-utility\test_tbl\Order-Date=20100101** , **s3-to-redshift-loader-utility\test_tbl\Order-Date=20100102** , **s3-to-redshift-loader-utility\test_tbl\Order-Date=20100103** , etc.
    4. Wait for the next run of AWS eventbridge **KickoffFileProcessingSchedule** and **QueueRSProcessingSchedule** and after that you should check the progress of the running copy command execution in Amazon DynamoDB table **s3_data_loader_log.copy_command_status**  the status for this column is "Execution", "Failed" or "Finished"

- #### Schema Detection     
    When deploying the CloudFormation template, the user has the option to enable schema detection. If this is enabled, a Lambda function will scan S3 file data to dynamically assess the file type, column structure, and data types to be loaded into Redshift. This is a BETA feature but the tool attempts to address most edge cases. If the schema detection fails, the copy command will proceed to attempt a load with the default parameters the user can configure when deploying the CloudFormation template.

    SHARED FEATURES & LIMITATIONS:
    - User can specify to enable/disable schema detection in CFN template
    - Automatic file type detection for the following files (file extension not needed): parquet, csv, json
    - Columns cannot contain standard data type keywords (Ex: TIMESTAMP)
    - Automatic DDL creation in Redshift cluster prior to load
    - Dynamic casting for integers based on size - (SMALLINT, INT, BIGINT)
    - Dynamic floating point number detection
    - Dynamic varchar columns based on max size of first 200,000 rows (3x factor)

    Following formats have been tested - Parquet, CSV, JSON. 

- #### Controlling Copy command parameters

    By default the copy command parameters are taken from the cloudformation input parameter **CopyCommandOptions** as defined in above Cloud Formation Parameters and it is stored in the DynamoDB table **s3_data_loader_table_config**

    To change or override the copy command options for any given table follow the steps as below

   
    1.  Go to DynamoDB and under **Tables** click on **Explore Items**
    2.  Select the table **s3_data_loader_table_config** and Click **Run** to scan the table data 
    3.  Click on the Table Name which you wish to overide and update the copy command options in **additional_copy_options**  e.g. To load a parquet        file    you can edit this field and change it to **format as parquet**
    4.  Click on **Save Changes**
    Once this is complete , all subsequent copy options will use the provided copy parameters while loading the data to Amazon Redshift. 
    
- #### Reloading files

    Files processed checkpoint is stored in the DynamoDb table **s3_data_loader_table_config** to reload files from an older timestamp do the following 
    1.  Go to DynamoDB and under **Tables** click on **Explore Items**
    2.  Select the table **s3_data_loader_table_config** and Click **Run** to scan the table data 
    3.  Click on the Table Name which you wish to overide and update the copy command options in **max_file_proccessed_timestamp**  e.g. To load         file   from the 7 PM 01/01/2022 you can edit this field and change it to **2022-01-01 19:00:00.000000**
    4.  Click on **Save Changes**


- #### Viewing Previous loads

    S3 loader process batch the files into manifest files and load to redshift. The COPY command and its progress is logged into  the DynamoDb table **s3_data_loader_log** . To check the previous loads and thier status

    1.  Go to DynamoDB and under **Tables** click on **Explore Items**
    2.  Select the table **s3_data_loader_log** and Click **Run** to scan the table data 
    3.  The field **copy_command_status** contains the status of the load , e.g. FAILED , COMPLETED etc.
    

- #### Viewing Current Loads

    S3 loader process batch the files into manifest files and load to redshift. The COPY command and its progress is logged into  the DynamoDb table **s3_data_loader_log** . To check the current loads and thier status

    1.  Go to DynamoDB and under **Tables** click on **Explore Items**
    2.  Select the table **s3_data_loader_log** and Click **Run** to scan the table data 
    3.  The field **copy_command_status** contains the status of the load , e.g. Execution
    
- #### Viewing Schedules in Event Bridge

    The s3 loader process has 2 event bridge engine that run on schedule ( default is every 5 mins). To check the next schedule or change follow the steps as below
    1. Go to Amazon EventBridge Console and click on **Rules**
    2. you would see an event bridge rule with names like **KickoffFileProcessingSchedule** , this is used to kick off the file processing and will check for new files and queue them for data load . By default it runs every 5 mins.
    3. you would see an event bridge rule with names like **QueueRSProcessingSchedule** , this is used to check the SQS Fifo Queue and execute the COPY Command /load data to redshift . By default it runs every 5 mins and process 5 copy commands at a time. This parameter is configureable and can be changed in the Lamda function **s3LoaderUtilProcessQueueLoadRS**
    4. To change any of the schedule , click on the rule name under **Event schedule** click on **Edit** , provide the updated schedule information or the cron expression and click Next (do not change anything else) and on last page click **Update Rule**

- #### Reviewing Logs

    S3 loader utility use multiple lambda function to process , queue and load file to Redshift. To check detailed logs refer to the cloud watch log group.
    1. Go to the cloud watch console and from the left navigation pane Expand **Logs** and then click on **Log Groups**
    2. In the log group search for log groups with keyword "s3LoaderUtil" , it will list all the logs generated by the S3 loader utility
    
- #### Pause and Resume the process

    S3 loader utility process can be paused and resumed for one or multiple tables by changing configurtion in DynamoDB table. The steps are as follows 

     1.  Go to DynamoDB and under **Tables** click on **Explore Items**
    2.  Select the table **s3_data_loader_table_config** and Click **Run** to scan the table data 
    3.  Click on the Table Name which you wish to overide and update the load status in **load_status**  e.g. To pause a table load set the value to "Inactive" and to resume the table load set it to "active"
    4.  Click on **Save Changes**


- #### Deleting the Framework

    If you would like to delete the framework please follow the steps as below 
    1. Go to the Cloudformation Console and click on the Hamburger Icon and select **Stacks** , look for the stack which was used to setup the s3 loader utility. 
    2. Select the stack and click on **Delete**
    3. Confirm the delete request by clicking on **Delete Stack** 

    The process will remove all the s3 loader utility componenets 

    Note : please note that the s3 loader utility create a directory on the s3 bucket to store the manifest files , they will NOT be removed by the process and neither the data files from Amazon S3 will be removed by the s3 loader utility. 
 


