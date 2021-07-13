from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.utils.task_group import TaskGroup
from airflow.providers.amazon.aws.hooks.sns import AwsSnsHook
from airflow.providers.amazon.aws.operators.sns import SnsPublishOperator
from datetime import datetime, timedelta
import os
import requests

CONN_ID = 'airflow-workshop'
BUCKET = 's3-landing-raw'
TARGET_SNS = Variable.get("sns_arn")

def upload_to_s3(endpoint, date):

    # s3 hook efetua uma instancia na AWS com boto3.
    s3_hook = S3Hook(aws_conn_id=CONN_ID)
    print("Created Connection")
    print(s3_hook.get_session())
    print(s3_hook)

    # Base URL
    url = 'https://covidtracking.com/api/v1/states/'

    res = requests.get(url+'{0}/{1}.csv'.format(endpoint, date))

    # Take string, upload to S3 using predefined method
    s3_hook.load_string(res.text, '{0}_{1}.csv'.format(endpoint, date), bucket_name=BUCKET, replace=True)

def on_failure_callback(context):
    op = SnsPublishOperator(
        task_id='failure',
        aws_conn_id=CONN_ID,
        target_arn=TARGET_SNS,
        message="Dag Sucessfull",
        subject="Dag Testing",
    )
    op.execute()

# Default settings aplicada a todas as tasks.
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': on_failure_callback,
    'region' : 'us-east-1'
}

endpoints = ['ca', 'co', 'ny', 'pa']
date = '{{ ds_nodash }}'
email_to = ['highenterprise2016@gmail.com']

with DAG('covid_data_to_s3',
         start_date=datetime(2019, 1, 1),
         max_active_runs=1,
         # https://airflow.apache.org/docs/stable/scheduler.html#dag-runs
         schedule_interval='@daily',
         on_failure_callback=on_failure_callback,
         default_args=default_args,
         catchup=False  # habilitar, senão quiser que dags historicas rodem
         ) as dag:


    t0 = DummyOperator(task_id='start')

    with TaskGroup('covid_task_group') as covid_group:
        for endpoint in endpoints:
            generate_files = PythonOperator(
                task_id='generate_file_{0}'.format(endpoint),
                python_callable=upload_to_s3,
                op_kwargs={'endpoint': endpoint, 'date': date}
            )
    
    send_email = SnsPublishOperator(
        task_id='covid_data_to_s3',
        aws_conn_id=CONN_ID,
        target_arn=TARGET_SNS,
        message="Dag Sucessfull",
        subject="Dag Testing",
    )


    t0 >> covid_group >> send_email