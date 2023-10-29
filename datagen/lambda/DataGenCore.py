import os
import sys
import json
import math
import random
import uuid
import time
from datetime import datetime, date
from decimal import Decimal
import re
import boto3
import pandas as pd
import numpy as np
from faker import Faker
from faker.providers import DynamicProvider

s3 = boto3.client('s3')
output_bucket = os.environ['OutputBucket']
today = datetime.today()
sensor_flag_true = 1
sensor_flag_false = 0

skill_provider = DynamicProvider(
    provider_name="skills",
    elements=["Python", "Pandas", "Linux", "SQL", "Data Mining"],
)

Department_provider = DynamicProvider(
    provider_name="Department",
    elements=["HR", "Analytics", "Finance", "Marketing", "Quality Assurance"],
)

Description_provider = DynamicProvider(
    provider_name="Description",
    elements=["HR", "Analytics", "Finance", "Marketing", "Quality Assurance"],
)

Department_list = ["HR", "Analytics", "Finance", "Marketing", "Quality Assurance"]

fake = Faker('en_US')
fake.add_provider(skill_provider)
fake.add_provider(Department_provider)
fake.add_provider(Description_provider)


def generate_random_data(lat, lon, num_rows):
    for _ in range(num_rows):
        hex1 = '%012x' % random.randrange(16 ** 12)  # 12 char random string
        flt = float(random.randint(0, 100))
        dec_lat = random.random() / 100
        dec_lon = random.random() / 100
        return ('%s %.1f %.6f %.6f \n' % (hex1.lower(), flt, lon + dec_lon, lat + dec_lat))

def f_schema(records, requesttype, inschema):
    fake = Faker('en_US')
    schema_bucket = os.environ['SchemaBucket']
    key = os.environ['Key']
    if inschema == 'N':
        key = requesttype + '-' + 'metadata.json'
        print(key)

    response = s3.get_object(Bucket=schema_bucket, Key=key)
    schema_file = response['Body']
    schema_data = json.loads(schema_file.read())
    column_list = schema_data['Columns']
    ColumnName = [sub['ColumnName'] for sub in column_list]
    DataType = [sub['Type'] for sub in column_list]
    table_name = schema_data['title']
    final_output_list = []

    # Batching logic start
    batchsize = int(os.environ['BatchSize'])
    loop = records // batchsize
    last_loop = records % batchsize
    l = []
    for i in range(loop):
        l.append(batchsize)
    l.append(last_loop)
    if 0 in l: l.remove(0)
    # Batching logic end

    temp_pd = pd.DataFrame()
    final_pd = pd.DataFrame()

    Description_provider = DynamicProvider(
        provider_name="Description",
        elements=["HR", "Analytics", "Finance", "Marketing", "Quality Assurance"],
    )

    fake.add_provider(Description_provider)

    for j in l:
        for i in range(j):
            # print(i)
            for each_col in column_list:
                column_name = each_col['ColumnName']
                column_type = each_col['Type']
                if column_name.lower().startswith('id') or column_name.lower().endswith('id'):
                    temp_pd[column_name] = [fake.uuid4()]

                elif column_type.lower() == "varchar":
                    if 'department' in column_name.lower():
                        temp_pd[column_name] = [random.choice(Department_list)]
                    elif 'name' in column_name.lower():
                        temp_pd[column_name] = [fake.name()]
                    elif 'location' in column_name.lower():
                        temp_pd[column_name] = [fake.address()]
                    elif 'description' in column_name.lower():
                        temp_pd[column_name] = [fake.text()[slice(30)]]

                elif column_type.lower() == "date":
                    if 'century' in column_name.lower():
                        temp_pd[column_name] = [fake.century()]
                    elif 'year' in column_name.lower():
                        temp_pd[column_name] = [fake.year()]
                    elif 'monthname' in column_name.lower():
                        temp_pd[column_name] = [fake.month_name()]
                    elif 'month name' in column_name.lower():
                        temp_pd[column_name] = [fake.month_name()]
                    elif 'day of week' in column_name.lower():
                        temp_pd[column_name] = [fake.day_of_week()]
                    elif 'dayofweek' in column_name.lower():
                        temp_pd[column_name] = [fake.day_of_week()]
                    elif 'day of month' in column_name.lower():
                        temp_pd[column_name] = [fake.day_of_month()]
                    elif 'dayofmonth' in column_name.lower():
                        temp_pd[column_name] = [fake.day_of_month()]
                    elif 'timezone' in column_name.lower():
                        temp_pd[column_name] = [fake.timezone()]
                    elif 'time zone' in column_name.lower():
                        temp_pd[column_name] = [fake.timezone()]
                    elif 'date of birth' in column_name.lower():
                        temp_pd[column_name] = [fake.date_of_birth()]
                    elif 'dateofbirth' in column_name.lower():
                        temp_pd[column_name] = [fake.date_of_birth()]
                    else:
                        temp_pd[column_name] = [
                            fake.date(pattern="%Y-%m-%d", end_datetime=date(today.year, 1, 1))]

                elif column_type.lower() == "double":
                    temp_pd[column_name] = [float(Decimal(random.randrange(5000, 20000)) / 100)]

                elif column_type.lower() == "boolean":
                    temp_pd[column_name] = random.randint(0, 1)

            final_pd = pd.concat([temp_pd, final_pd], ignore_index=True)

        ## parameterize this list
        # dfs=pd.DataFrame(final_output_list, columns=c_name)
        js = final_pd.to_json(orient="records")
        # fileName = table_name + '/' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '/' + str(uuid.uuid4()) + '.json '
        fileName = table_name + '/' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '.json '
        s3.put_object(Bucket=output_bucket, Key=fileName, Body=js)
        final_output_list = []

    return (final_pd)


def handler(event, context):
    DataRequestType = os.environ['DataRequestType']
    InSchema = os.environ['InSchema']
    DataRequestSize = int(os.environ['DataRequestSize'])
    try:
        start = time.time()
        if DataRequestType == 'iot' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif DataRequestType.lower() == 'finance' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif DataRequestType.lower() == 'hr' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif DataRequestType.lower() == 'hr-personal' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif DataRequestType.lower() == 'banking' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif DataRequestType.lower() == 'automotive' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif DataRequestType.lower() == 'sales' and InSchema == 'N':
            f_schema(DataRequestSize, DataRequestType, InSchema)
        elif InSchema.upper() == 'Y':
            dfs1 = f_schema(DataRequestSize, DataRequestType, InSchema)
            print(dfs1)
        end = time.time()
        print('Time taken to generate ' + DataRequestType + ' is ' + str(end - start) + ' seconds')

    except Exception as err:
        print(err)