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
            dbname = 'Gold_Fintech',
            user ='postgres',
            password ='Chinwe31#',
            host ='localhost',
            port ='5432'
        )
        print("Connection established successfully.")
        return connection
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        return None
