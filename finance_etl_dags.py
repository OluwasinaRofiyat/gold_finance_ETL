from airflow import DAG
from datetime import timedelta, datetime
from airflow.operators.dummy_operator import DummyOperator
import pandas as pd
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from modules.extract import get_max_date_from_staging, fetch_alpha_vantage_data
from modules.extract_test import test_api_schema, test_sample_data
from modules.transform import transform_and_write_to_csv
from modules.transform_test import test_transformations
from modules.load import batch_insert, exec_procedure
from modules.load_test import test_load_row_count, test_db_columns
from modules.helpers import get_db_connection
from sqlalchemy.orm import sessionmaker

# Connection setup
connection = get_db_connection()
engine = create_engine("postgresql://postgres:Chinwe31#@localhost:5432/Gold_Fintech")
connection_string = "postgresql://postgres:Chinwe31#@localhost:5432/Gold_Fintech"
table_name = "alpha_vantage.staging_finance_data"

# Getting max date from DB
max_date_from_db = get_max_date_from_staging(connection_string, table_name)

# Symbols and API key
symbols = ['TSCO.LON', 'IBM', 'MBG.DEX', 'SHOP.TRT']
api_key = "ML7BZYF38ZPZLHR4"


    
# Assuming you still have your transform logic to work on the df_combined
df_combined = pd.read_csv('./landing_data/alpha_vantage.csv')
output_path = './data/alpha_vantage_transformed_data.csv'
transform_and_write_to_csv(df_combined, output_path)

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
dag = DAG(
    dag_id='Financial_data_analysis_ETL_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

# Define the tasks
start_pipeline = DummyOperator(task_id="tsk_start_pipeline", dag=dag)

get_max_date_from_staging_table_task = PythonOperator(
    task_id="get_max_date",
    python_callable=get_max_date_from_staging,
    op_kwargs={'connection_string': connection_string, 'table_name': table_name},
    dag=dag
)

# Loop over symbols and create extract tasks for each
extract_tasks = []
for symbol in symbols:
    extract_task = PythonOperator(
        task_id=f"extract_{symbol}",
        python_callable=fetch_alpha_vantage_data,
        op_kwargs={'symbol': symbol, 'api_key': api_key, 'max_date_from_db': max_date_from_db},
        dag=dag
    )
    extract_tasks.append(extract_task)

# Test API schema
api_test_task = PythonOperator(
    task_id="api_test",
    python_callable=test_api_schema,
    dag=dag
)

extract_test_task = PythonOperator(
    task_id="extract_test",
    python_callable=test_sample_data,
    dag=dag
)

transform_task = PythonOperator(
    task_id="transform",
    python_callable=transform_and_write_to_csv,
    provide_context=True,  # Required for XComs
    dag=dag
)


transform_test_task = PythonOperator(
    task_id="transform_test",
    python_callable=test_transformations,
    dag=dag
)

load_staging_task = PythonOperator(
    task_id="load_staging_task",
    python_callable=batch_insert,
    op_kwargs={'df': pd.DataFrame(), 'table_name': table_name, 'connection': connection},  # Add a placeholder for `df`
    dag=dag
)

prod_db_task = PythonOperator(
    task_id="prod_db",
    python_callable=exec_procedure,
    op_kwargs={'engine': engine},
    dag=dag
)

test_load_row_count_task = PythonOperator(
    task_id="test_load_row_count",
    python_callable=test_load_row_count,
    dag=dag
)

test_db_columns_task = PythonOperator(
    task_id="test_db_columns",
    python_callable=test_db_columns,
    dag=dag
)

end_pipeline = DummyOperator(task_id="tsk_end_pipeline", dag=dag)

# Task dependencies
start_pipeline >> get_max_date_from_staging_table_task >> extract_tasks >> api_test_task >> extract_test_task >> transform_task >> transform_test_task >> load_staging_task >> prod_db_task >> test_load_row_count >> test_db_columns_task >> end_pipeline
