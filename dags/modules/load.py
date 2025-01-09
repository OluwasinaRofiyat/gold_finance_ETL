
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Define function to get database connection using PostgresHook
def get_db_connection(postgres_conn_id):
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        connection = hook.get_conn()
        print("Connection established successfully.")
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None

# Batch insert data into PostgreSQL
def batch_insert(df, table_name, postgres_conn_id):
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    connection = hook.get_conn()
    cursor = connection.cursor()
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))
    query = f"INSERT INTO {table_name} ({cols}) VALUES %s"

    try:
        from psycopg2.extras import execute_values
        execute_values(cursor, query, tuples)
        connection.commit()
        print(f"Data inserted successfully into {table_name}")
    except Exception as e:
        print(f"Error inserting data into {table_name}: {e}")
        connection.rollback()
    finally:
        cursor.close()

# Execute stored procedure
def exec_procedure(postgres_conn_id):
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    engine = hook.get_sqlalchemy_engine()
    session = sessionmaker(bind=engine)()
    try:
        session.execute(text('CALL "alpha_vantage".prc_financedata();'))
        session.commit()
        print("Procedure executed successfully.")
    except Exception as e:
        print(f"Error executing procedure: {e}")
        session.rollback()
    finally:
        session.close()

