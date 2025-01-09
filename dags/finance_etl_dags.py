from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import timedelta, datetime
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
import requests
import pytest
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from modules.extract import get_max_date_from_staging, fetch_alpha_vantage_data
from modules.extract_test import validate_api_response
from modules.transform import apply_data_quality_checks
from modules.transform_test import test_data_transformation
from modules.load import batch_insert, exec_procedure
from modules.load_test import test_postgres_connection
from modules.helpers import get_db_connection
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pyspark.sql import SparkSession
import psycopg2
from psycopg2 import sql
import os
import subprocess
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import StructType, StructField, DateType, DoubleType, IntegerType, StringType
from pyspark.sql.window import Window

#from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
load_dotenv()

# Define your PostgreSQL connection string
#connection_string  = "postgresql+psycopg2://{{ var.value.get('user') }}:{{ var.value.get('password') }}@{{ var.value.get('host') }}:5432/{{ var.value.get('dbname') }}"

from airflow.hooks.postgres_hook import PostgresHook

#postgres_connection_string = "postgresql+psycopg2://postgres:Chinwe31%23@host.docker.internal:5432/Gold_Fintech"

# Use the connection string in the PostgresHook or similar setup
#postgres_hook = PostgresHook(postgres_conn_id='on_prem_postgres', sql_conn_str=postgres_connection_string)



# Define the table name in the staging area
#table_name = "alpha_vantage.staging_finance_data"

# Get the maximum date from the PostgreSQL staging table
#max_date_from_db = get_max_date_from_staging(connection_string, table_name)

# Define the list of symbols and your API key
#symbols = ['TSCO.LON', 'IBM', 'MBG.DEX', 'SHOP.TRT']
#api_key = "ML7BZYF38ZPZLHR4"

# Empty list to collect all dataframes
#df_list = []

# Looping through the symbols and fetching data for each
#for symbol in symbols:
    #df_symbol = fetch_alpha_vantage_data(symbol, api_key, max_date_from_db)
    #df_list.append(df_symbol)

# Concatenate all dataframes into one
#df_combined = pd.concat(df_list, ignore_index=True)

# Display the first few rows of the combined dataframe
#print(df_combined.head())



# Save the combined dataframe to CSV
#df_combined.to_csv('./alpha_vantage.csv', index=False)

#output_path = './alpha_vantage_transformed.csv'
#transform_and_write_to_csv()

#df = pd.read_csv("./alpha_vantage_transformed.csv", delimiter=',')

# Convert PySpark DataFrame to Pandas DataFrame for use with psycopg2
#df = df_spark.toPandas()

# Specify table name
#table_name = 'alpha_vantage.staging_finance_data'

# Establish connection
#connection = get_db_connection()

# Perform batch insert if connection is established
#if connection:
    #batch_insert(df, table_name, connection)
    
#engine = create_engine("postgresql://postgres:Chinwe31#@host.docker.internal:5432/Gold_Fintech")

#dbname = 'Gold_Fintech',
#user ='postgres',
#password ='Chinwe31#',
#host ='localhost',
#port ='5432'
# Close the connection


# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 11, 17),
    'email': ['myemail@domain.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(seconds=10)
}

# DAG definition
with DAG(
    dag_id='Gold_finance_ETL_pipeline',
    default_args=default_args,
    description='Pipeline for loading and processing finance data',
    schedule_interval=None,
    catchup=False,
) as dag:

# Define the tasks
    start_pipeline = DummyOperator(task_id="tsk_start_pipeline", dag=dag)

    
    symbol = 'IBM'  # Replace with desired stock symbol
    api_key = "ML7BZYF38ZPZLHR4"  # Replace with your actual API key
    
    api_test_task = PythonOperator(
        task_id='api_test',
        python_callable=validate_api_response,
        op_args=[symbol, api_key],
        dag=dag,
    )
    
    
    
    pg_hook = PostgresHook(postgres_conn_id='on_prem_postgres', schema='Gold_Fintech')
    connection = pg_hook.get_conn()
    cursor = connection.cursor()
    
    
    connection.commit()
    cursor.close()
    connection.close()
# PythonOperator to run the get_max_date_from_staging function
    fetch_max_date_task = PythonOperator(
        task_id='fetch_max_date',
        python_callable=get_max_date_from_staging,
        op_kwargs={
            'postgres_conn_id': 'my_postgres_connection',  # Replace with your connection ID
            'table_name': 'alpha_vantage.staging_finance_data',           # Replace with your table name
        },
    )

    def extract_data(**kwargs):
        # Define your inputs
        symbols = ['TSCO.LON', 'IBM', 'MBG.DEX', 'SHOP.TRT']
        #api_key = "ML7BZYF38ZPZLHR4"
        api_key =  "KA3DQ2SRS8MOUN8J"
        max_date_from_db = datetime(2023, 1, 1)  # Replace with actual query to get max date

        # Fetch data for each symbol
        df_list = []
        for symbol in symbols:
            df_symbol = fetch_alpha_vantage_data(symbol, api_key, max_date_from_db)
            df_list.append(df_symbol)

        # Combine all DataFrames
        df_combined = pd.concat(df_list, ignore_index=True)

        # Save DataFrame to a CSV file (can also be pushed to S3 or a database)
        output_path = './alpha_vantage.csv'  # Adjust path as needed
        df_combined.to_csv(output_path, index=False)

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )


    script_transform_test_path = '/home/rita/Finance_ETL/myenv/dags/modules/transform_test.py'        
            
    def run_pyspark_test_script(**kwargs):
        os.system(f"spark-submit {script_transform_test_path}")        
            
    # Task to run the pytest tests
    run_transform_tests_task = PythonOperator(
        task_id='run_unittest_transform_tests_task',
        python_callable=run_pyspark_test_script
    )
    
    script_path = '/home/rita/Finance_ETL/myenv/dags/modules/transform.py'


# Define the PythonOperator to execute the transformation script
    def run_pyspark_script(**kwargs):
        os.system(f"spark-submit {script_path}")

    transform_task = PythonOperator(
        task_id='transform_alpha_vantage_data',
        python_callable=run_pyspark_script,
        dag=dag
)
    
    
    

# Function to run pytest from Airflow DAG
    #def run_pytest_tests():
    # Execute the pytest command from within the DAG
        #result = subprocess.run(
            #["pytest", "/dags/modules/transform.py", "--maxfail=1", "--disable-warnings", "-q"],
            #stdout=subprocess.PIPE,
            #stderr=subprocess.PIPE
        #)
    
    # Print the test results for logging purposes
        #print(result.stdout.decode())
        #print(result.stderr.decode())
    
    # Raise an error if the tests failed
        #if result.returncode != 0:
            #raise Exception(f"Tests failed with return code {result.returncode}")
        #else:
            #print("Tests passed!")
    
        
        



#transform_spark_task = SparkSubmitOperator(
    #task_id="transform_spark_job",
    #application= 'transform_and_write_to_csv',
    #conf={'spark.master': 'yarn'},  # Change to 'spark.kubernetes' or 'spark.standalone' as appropriate
#jars='path/to/dependencies.jar',  # If additional jars are required
    #conn_id='spark_default'  # Spark connection configured in Airflow
    #dag=dag
#)

# Path to the transformation script
    

    test_connection_task = PythonOperator(
        task_id="test_postgres_connection_task",
        python_callable=test_postgres_connection,
    )

# Input and database configurationsalpha_vantage_transformed.csv
    input_csv_path = "./alpha_vantage_transformed"
    table_name = 'alpha_vantage.staging_finance_data'
#engine_url = 'postgresql://postgres:Chinwe31#@localhost:5432/Gold_Fintech'



# Task to batch insert data
    def insert_data_to_postgres(**kwargs):
        # Example dataframe
        
            df = pd.read_csv(input_csv_path, delimiter=',')
            batch_insert(df, 'alpha_vantage.staging_finance_data', postgres_conn_id='my_postgres_connection')

    insert_task = PythonOperator(
            task_id='batch_insert_data',
            python_callable=insert_data_to_postgres,
    )

    # Task to execute stored procedure
    exec_proc_task = PythonOperator(
            task_id='execute_procedure',
            python_callable=exec_procedure,
            op_kwargs={'postgres_conn_id': 'my_postgres_connection'},
    )

    # Task: Test Postgres connection
    



    end_pipeline = DummyOperator(task_id="tsk_end_pipeline", dag=dag)

# Task dependencies
    start_pipeline >> api_test_task >> fetch_max_date_task >> extract_task >> run_transform_tests_task >> transform_task >> test_connection_task >> insert_task >> exec_proc_task  >> end_pipeline
