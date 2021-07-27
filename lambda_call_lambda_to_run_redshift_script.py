import json
import boto3
import cfnresponse

def handler(event, context):
    print(event)
    if event['RequestType'] == 'Delete':
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Data': 'No Action Needed'})
    # Check if this is a Create and we're failing Creates
    elif event['RequestType'] == 'Create' and event['ResourceProperties'].get('FailCreate', False):
        raise RuntimeError('Create failure requested')
    else:
        action = event['ResourceProperties']['Action']
        redshift_host = event['ResourceProperties']['RedshiftHost']
        redshift_db = event['ResourceProperties']['RedshiftDb']
        redshift_user = event['ResourceProperties']['RedshiftUser']
        script_s3_path = event['ResourceProperties']['ScriptS3Path']
        redshift_iam_role = event['ResourceProperties']['RedshiftIamRole']
        lambda_arn = event['ResourceProperties']['LambdaArn']
        lambda_payload = {
            "input": {
                "Action": action,
                "RedshiftHost": redshift_host,
                "RedshiftDb": redshift_db,
                "RedshiftUser": redshift_user,
                "RedshiftIamRole": redshift_iam_role,
                "ScriptS3Path": script_s3_path,
                "redshift_iam_role": redshift_iam_role
            }
        }
        response = boto3.client('lambda').invoke(
            FunctionName=lambda_arn,
            InvocationType='Event',
            Payload=json.dumps(lambda_payload)
        )
        print(response)
        cfnresponse.send(event, context, cfnresponse.SUCCESS, {'Data': 'Create complete'})

if __name__ == "__main__":
    event ={
	'RequestType': 'Create',
	'ServiceToken': 'arn:aws:lambda:us-east-1:855402123041:function:redshift-demo-redshift-bo-SingletonLambda130c8acc4-NLBM0M7107K',
	'ResponseURL': 'https://cloudformation-custom-resource-response-useast1.s3.amazonaws.com/arn%3Aaws%3Acloudformation%3Aus-east-1%3A855402123041%3Astack/redshift-demo-redshift-bootstrap-stack2/89df0570-a250-11eb-84de-0a43cdcd5209%7CcustomResourceLambdaCallRunRedshiftScript%7C51ca3d8a-e891-4e35-a840-bc0ef5ccfc9d?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20210421T032106Z&X-Amz-SignedHeaders=host&X-Amz-Expires=7200&X-Amz-Credential=AKIA6L7Q4OWTYMT6AIEY%2F20210421%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Signature=650a79b649f7971b784a4685fc7af602b75c3dcbc401119b433a6cf28b99bd5b',
	'StackId': 'arn:aws:cloudformation:us-east-1:855402123041:stack/redshift-demo-redshift-bootstrap-stack2/89df0570-a250-11eb-84de-0a43cdcd5209',
	'RequestId': '51ca3d8a-e891-4e35-a840-bc0ef5ccfc9d',
	'LogicalResourceId': 'customResourceLambdaCallRunRedshiftScript',
	'ResourceType': 'AWS::CloudFormation::CustomResource',
	'ResourceProperties': {
		'ServiceToken': 'arn:aws:lambda:us-east-1:855402123041:function:redshift-demo-redshift-bo-SingletonLambda130c8acc4-NLBM0M7107K',
		'Action': 'RUN_REDSHIFT_SCRIPT',
		'RedshiftHost': 'redshift-demo-redshift-stack-redshiftcluster-wo73jo4zwwtg.cxzy7wkirtem.us-east-1.redshift.amazonaws.com',
		'LambdaArn': 'arn:aws:lambda:us-east-1:855402123041:function:redshift-demo-redshift-bo-lambdaRunRedshiftScript0-4EKDBQRJD21F',
		'RedshiftIamRole': 'arn:aws:iam::855402123041:role/redshift-demo-redshift-st-redshiftClusterRole4D302-1I44UET6SAEVE',
		'RedshiftDb': 'dev',
		'ScriptS3Path': 's3://event-driven-app-with-lambda-redshift/scripts/test_script.sql',
		'RedshiftUser': 'awsuser'
	}
}

    context = ""
    handler(event, context)

