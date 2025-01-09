from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import os
import glob
import pandas as pd
from modules.extract_test import validate_api_response
from modules.extract import get_max_date_from_staging, fetch_alpha_vantage_data
from modules.transform import apply_data_quality_checks, transform_and_write_to_csv
from modules.load import batch_insert, exec_procedure
from airflow.operators.bash import BashOperator

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=10),
    'start_date': datetime(2023, 11, 17),
}

# Define the DAG
with DAG(
    dag_id='gold_finance_data_pipeline',
    default_args=default_args,
    schedule_interval=None,
    description="ETL Pipeline for finance data",
    catchup=False,
) as dag:

    # Start pipeline
    start_pipeline = DummyOperator(task_id="start_pipeline")

    # Test API response
    def validate_api():
        symbol = "IBM"
        api_key = "ML7BZYF38ZPZLHR4"
        validate_api_response(symbol, api_key)

    api_test_task = PythonOperator(
        task_id='api_test_task',
        python_callable=validate_api,
    )


    # Fetch maximum date from staging
    fetch_max_date_task = PythonOperator(
        task_id='fetch_max_date_task',
        python_callable=get_max_date_from_staging,
        op_kwargs={'postgres_conn_id': 'my_postgres_connection', 
                   'table_name': 'alpha_vantage.staging_finance_data'},
    )

    # Extract data from API
    def extract_data():
        symbols = ['TSCO.LON', 'IBM', 'MBG.DEX', 'SHOP.TRT']
        api_key = "ML7BZYF38ZPZLHR4"
        max_date_from_db = datetime(2023, 1, 1)
        df_list = [fetch_alpha_vantage_data(symbol, api_key, max_date_from_db) for symbol in symbols]
        df_combined = pd.concat(df_list, ignore_index=True)
        df_combined.to_csv('/tmp/alpha_vantage.csv', index=False)

    extract_data_task = PythonOperator(
        task_id='extract_data_task',
        python_callable=extract_data,
    )

    # Run transformation (PySpark job)
    #transform_task = SparkSubmitOperator(
        #task_id='transform_data_task',
        #application='/home/rita/Finance_ETL/myenv/dags/modules/transform.py',
        ##conn_id='spark_default',
        #verbose=True,
    #)

    transform_task = PythonOperator(
    task_id='pyspark_task',
    python_callable=transform_and_write_to_csv,
    provide_context=True
    )

    # Load data into Postgres
    def load_data_to_postgres():
        files = glob.glob('/tmp/spark_output/*.csv')
        if files:
            selected_file = files[0]  # Select the first CSV file
            print(f"Reading: {selected_file}")
        else:
            raise FileNotFoundError("No CSV files found in the /tmp/spark_output")
    
    # Read the selected CSV file into a pandas DataFrame
        df = pd.read_csv(selected_file)
        batch_insert(df, 'alpha_vantage.staging_finance_data', postgres_conn_id='my_postgres_connection')

    load_data_task = PythonOperator(
        task_id='load_data_task',
        python_callable=load_data_to_postgres,
    )

    # Execute Postgres procedure
    exec_proc_task = PythonOperator(
        task_id='execute_procedure_task',
        python_callable=exec_procedure,
        op_kwargs={'postgres_conn_id': 'my_postgres_connection'},
    )

    # End pipeline
    end_pipeline = DummyOperator(task_id="end_pipeline")

    # Task Dependencies
    start_pipeline >> api_test_task >> fetch_max_date_task >> extract_data_task >> transform_task >> load_data_task >> exec_proc_task >> end_pipeline

    #start_pipeline >> transform_task >> load_data_task >> exec_proc_task >> end_pipeline