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

Department_list = ["HR", "Analytics", "Finance", "Marketing", "Quality Assurance"]

fake = Faker('en_US')
fake.add_provider(skill_provider)
fake.add_provider(Department_provider)


def generate_random_data(lat, lon, num_rows):
    for _ in range(num_rows):
        hex1 = '%012x' % random.randrange(16 ** 12)  # 12 char random string
        flt = float(random.randint(0, 100))
        dec_lat = random.random() / 100
        dec_lon = random.random() / 100
        return ('%s %.1f %.6f %.6f \n' % (hex1.lower(), flt, lon + dec_lon, lat + dec_lat))


def f_schema_less(records, request_type):
    iot = []

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

    if request_type == 'iot':
        for j in l:
            iot = []
            for i in range(j):
                sensor_id = str(uuid.uuid4())
                sensor_name = fake.name()
                sensor_description = fake.last_name()
                table_name = 'iot'
                v_latitude = float(random.randint(0, 100))
                v_longitude = float(random.randint(0, 100))

                iot.append({
                    "Sensor Id": sensor_id,
                    "Sensor Name": sensor_name,
                    "Sensor Description": sensor_description,
                    "Sensor Installed Date": fake.date(pattern="%Y-%m-%d", end_datetime=date(today.year, 1, 1)),
                    "Lattitude": generate_random_data(v_latitude, v_longitude, 1)[3],
                    "Longitude": generate_random_data(v_latitude, v_longitude, 1)[2],
                    "Location Name": fake.address(),
                    "Sensor Captured Date": fake.date(pattern="%Y-%m-%d", end_datetime=date(today.year, 1, 1)),
                    "Sensor 1": sensor_flag_true,
                    "Sensor 2": sensor_flag_false,
                    "Sensor 3": sensor_flag_true,
                    "Sensor 4": sensor_flag_false,
                    "Sensor 5": sensor_flag_true,
                    "Sensor 6": sensor_flag_false,
                    "Sensor 7": sensor_flag_true,
                    "Sensor 8": sensor_flag_false,
                    "Sensor 9": sensor_flag_true,
                    "Sensor 10": sensor_flag_false,
                    "Sensor 11": sensor_flag_true,
                    "Sensor 12": sensor_flag_false
                })

            js = json.dumps(iot, indent=4, separators=(',', ': '), sort_keys=False)
            fileName = table_name + '_noschema/' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '/' + str(
                uuid.uuid4()) + '.json '
            s3.put_object(Bucket=output_bucket, Key=fileName, Body=js)

    # elif request_type=='finance':
    # elif request_type=='hr':
    # elif request_type=='hr-personal':
    # elif request_type=='banking':
    # elif request_type=='automotive':
    # elif request_type=='sales':


def f_schema(records):
    fake = Faker('en_US')
    schema_bucket = os.environ['SchemaBucket']
    key = os.environ['Key']

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

    for j in l:
        for i in range(j):
            # print(i)
            for each_col in column_list:
                column_name = each_col['ColumnName']
                column_type = each_col['Type']
                if column_name.lower() == "id":
                    temp_pd[column_name] = [fake.uuid4()]

                elif column_type.lower() == "varchar":
                    if column_name == 'Department':
                        temp_pd[column_name] = [random.choice(Department_list)]
                    elif column_name == 'Name':
                        temp_pd[column_name] = [fake.name()]
                    elif column_name == 'Location':
                        temp_pd[column_name] = [fake.address()]

                elif column_type.lower() == "date":
                    temp_pd[column_name] = [
                        fake.date(pattern="%Y-%m-%d", end_datetime=date(today.year, 1, 1))]

                elif column_type.lower() == "double":
                    temp_pd[column_name] = [float(Decimal(random.randrange(5000, 20000)) / 100)]

            final_pd = pd.concat([temp_pd, final_pd], ignore_index=True)

        ## parameterize this list
        # dfs=pd.DataFrame(final_output_list, columns=c_name)
        js = final_pd.to_json(orient="records")
        fileName = table_name + '_schema/' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '/' + str(
            uuid.uuid4()) + '.json '
        s3.put_object(Bucket=output_bucket, Key=fileName, Body=js)
        final_output_list = []

    return (final_pd)

def handler(event, context):
    # DataRequestType = event['DataRequestType'].lower()
    # InSchema = event['InSchema']
    # DataRequestSize = int(event['DataRequestSize'])

    DataRequestType = os.environ['DataRequestType']
    InSchema = os.environ['InSchema']
    DataRequestSize = int(os.environ['DataRequestSize'])
    try:
        start = time.time()
        if DataRequestType == 'iot' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif DataRequestType.lower() == 'finance' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif DataRequestType.lower() == 'hr' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif DataRequestType.lower() == 'hr-personal' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif DataRequestType.lower() == 'banking' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif DataRequestType.lower() == 'automotive' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif DataRequestType.lower() == 'sales' and InSchema == 'N':
            f_schema_less(DataRequestSize, DataRequestType)
        elif InSchema == 'Y':
            dfs1 = f_schema(DataRequestSize)
            print(dfs1)
        end = time.time()
        print('Time taken to generate ' + DataRequestType + ' is ' + str(end - start) + ' seconds')

    except Exception as err:
        print(err)