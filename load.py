
import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_db_connection():
    """
    Establish a connection to the PostgreSQL database.
    """
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('PG_DBNAME'),
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT')
        )
        print("Connection established successfully.")
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None

def batch_insert(df, table_name, connection):
    """
    Insert data from a Pandas DataFrame into a PostgreSQL table in batch.
    
    :param df: Pandas DataFrame to be inserted
    :param table_name: Target table name in PostgreSQL
    :param connection: Active database connection
    """
    if not connection:
        print("No database connection.")
        return

    cursor = connection.cursor()
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))
    query = f"INSERT INTO {table_name} ({cols}) VALUES %s"

    try:
        extras.execute_values(cursor, query, tuples)
        connection.commit()
        print(f"Data inserted successfully into {table_name}")
    except Exception as e:
        print(f"Error inserting data into {table_name}: {e}")
        connection.rollback()
    finally:
        cursor.close()
        
def exec_procedure(engine):
    session = sessionmaker(bind = engine)
    session=session()
    session.execute('CALL "alpha_vantage".prc_financedata()')
    session.commit

def close_connection(connection):
    """
    Close the database connection.
    """
    if connection:
        connection.close()
        print("Database connection closed.")

# Initialize Spark session
#spark = SparkSession.builder.appName("Financial Data").getOrCreate()

# Read CSV file into PySpark DataFrame
df = pd.read_csv("/root/data/alpha_vantage_transformed_data.csv/part-00000-6a5c419e-0abf-4703-a3dc-982d48eba4f1-c000.csv", delimiter=',')

# Convert PySpark DataFrame to Pandas DataFrame for use with psycopg2
#df = df_spark.toPandas()

# Specify table name
table_name = 'alpha_vantage_finance.staging_alpha_finance'

# Establish connection
connection = get_db_connection()

# Perform batch insert if connection is established
if connection:
    batch_insert(df, table_name, connection)

# Close the connection
close_connection(connection)