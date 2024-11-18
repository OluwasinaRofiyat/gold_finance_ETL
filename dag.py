from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
import asyncio

# Import modules
from extract import fetch_all_data
from transform import process_data
from load import load_data_to_postgres

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the DAG
with DAG(
    'daily_finance_etl',
    default_args=default_args,
    description='ETL pipeline for daily finance data',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
) as dag:

    # Extract and Transform Task
    def extract_transform_task(**context):
        symbols = ['TSCO.LON', 'IBM', 'MBG.DEX', 'SHOP.TRT']  # Example stock symbols
        responses = asyncio.run(fetch_all_data(symbols))
        data = asyncio.run(process_data(symbols, responses))
        context['ti'].xcom_push(key='processed_data', value=data)

    # Load Task
    def load_task(**context):
        data = context['ti'].xcom_pull(key='processed_data', task_ids='extract_transform')
        load_data_to_postgres(data)

    extract_transform = PythonOperator(
        task_id='extract_transform',
        python_callable=extract_transform_task,
        provide_context=True
    )

    load = PythonOperator(
        task_id='load_to_postgres',
        python_callable=load_task,
        provide_context=True
    )

    extract_transform >> load
