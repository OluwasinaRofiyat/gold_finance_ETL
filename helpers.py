import os
import psycopg2
from psycopg2 import extras
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file
load_dotenv()


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
