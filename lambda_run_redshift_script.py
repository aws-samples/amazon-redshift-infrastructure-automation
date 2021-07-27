import boto3
import traceback

def handler(event, context):
    print(event)
    action = event['input'].get('Action')
    redshift_host = event['input'].get('RedshiftHost')
    redshift_db = event['input'].get('RedshiftDb')
    redshift_user = event['input'].get('RedshiftUser')
    redshift_iam_role = event['input'].get('RedshiftIamRole')
    script_s3_path = event['input'].get('ScriptS3Path')
    sql_query_id = event['input'].get('sql_query_id')

    try:
        if action == "RUN_REDSHIFT_SCRIPT":
            res = {'sql_id': run_sql(redshift_host, redshift_db, redshift_user, redshift_iam_role, script_s3_path)}
        elif action == "SQL_STATUS":
            res = {'status': sql_status(sql_query_id)}
        else:
            raise ValueError("Invalid Task: " + action)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise
    print(res)
    return res


def get_config_from_s3(script_s3_path):
    path_parts = script_s3_path.replace("s3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)
    obj = boto3.client('s3').get_object(Bucket=bucket, Key=key)
    return obj['Body'].read().decode('utf-8')


def run_sql(redshift_host, redshift_db, redshift_user, redshift_iam_role, script_s3_path, with_event=True,
            run_type='ASYNC'):
    cluster_identifier = redshift_host.split('.')[0]
    script = get_config_from_s3(script_s3_path).format(redshift_iam_role)

    res = boto3.client("redshift-data").execute_statement(Database=redshift_db, DbUser=redshift_user, Sql=script,
                                                          ClusterIdentifier=cluster_identifier, WithEvent=with_event)
    query_id = res["Id"]
    statuses = ["STARTED", "FAILED", "FINISHED"] if run_type == 'ASYNC' else ["FAILED", "FINISHED"]
    done = False
    while not done:
        status = sql_status(query_id)
        if status in statuses:
            print(query_id + ":" + status)
            break
    return query_id


def sql_status(query_id):
    res = boto3.client("redshift-data").describe_statement(Id=query_id)
    status = res["Status"]
    if status == "FAILED":
        raise Exception('Error:' + res["Error"])
    return status.strip('"')


if __name__ == "__main__":
    event ={
	'input': {
		'Action': 'RUN_REDSHIFT_SCRIPT',
		'RedshiftHost': 'redshift-demo-redshift-stack-redshiftcluster-wo73jo4zwwtg.cxzy7wkirtem.us-east-1.redshift.amazonaws.com',
		'RedshiftDb': 'dev',
		'RedshiftUser': 'awsuser',
		'RedshiftIamRole': 'arn:aws:iam::855402123041:role/redshift-demo-redshift-st-redshiftClusterRole4D302-1I44UET6SAEVE',
		'ScriptS3Path': 's3://event-driven-app-with-lambda-redshift/scripts/test_script.sql',
		'redshift_iam_role': 'arn:aws:iam::855402123041:role/redshift-demo-redshift-st-redshiftClusterRole4D302-1I44UET6SAEVE'
	}
}

    context = ""
    handler(event, context)

