import requests
import pandas as pd
import psycopg2
from psycopg2 import sql
import os

from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, IntegerType, StructField, StringType, DoubleType, DateType

# Function to get the max date from the PostgreSQL staging table
# Function to fetch the maximum date from a staging table
def get_max_date_from_staging(**kwargs):
    postgres_conn_id = kwargs['postgres_conn_id']
    table_name = kwargs['table_name']
    
    # Query to get the maximum date
    query = f"SELECT MAX(date) FROM {table_name};"
    
    try:
        # Use PostgresHook to connect and execute the query
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        connection = hook.get_conn()
        cursor = connection.cursor()
        cursor.execute(query)
        max_date = cursor.fetchone()[0]
        cursor.close()
        connection.close()

        # Return the max date or a default value
        return max_date if max_date else datetime(2000, 1, 1)
    
    except Exception as e:
        print(f"Error fetching max date: {e}")
        return datetime(2000, 1, 1)


def fetch_alpha_vantage_data(symbol, api_key, max_date_from_db):
    """
    Fetch daily stock data for a given symbol from the Alpha Vantage API and return as a DataFrame.
    
    Parameters:
    symbol (str): Stock ticker symbol (e.g., "AAPL" for Apple Inc.).
    api_key (str): API key for Alpha Vantage.
    max_date_from_db (datetime): Maximum date from the staging table to control data extraction.
    
    Returns:
    - pd.DataFrame: DataFrame with the time series data for the symbol.
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    # Extracting metadata
    meta_data = data.get('Meta Data', {})
    description = meta_data.get('1. Information', '')
    last_refreshed = meta_data.get('3. Last Refreshed', '')
    output_size = meta_data.get('4. Output Size', 'N/A')
    time_zone = meta_data.get('5. Time Zone', 'N/A')
    symbol = meta_data.get('2. Symbol', '')
    
    # Initializing empty lists for time series data
    dates, opens, highs, lows, closes, volumes = [], [], [], [], [], []
    
    # Iterate over daily data
    for date, daily_data in data.get('Time Series (Daily)', {}).items():
        # Convert date to datetime
        date = datetime.strptime(date, '%Y-%m-%d')
        
        # Only add data if the date is greater than the max date from the staging table
        if date > max_date_from_db:
            dates.append(date)
            opens.append(float(daily_data.get('1. open', 0)))
            highs.append(float(daily_data.get('2. high', 0)))
            lows.append(float(daily_data.get('3. low', 0)))
            closes.append(float(daily_data.get('4. close', 0)))
            volumes.append(int(daily_data.get('5. volume', 0)))
    
    # Creating DataFrame
    df = pd.DataFrame({
        'date': dates,
        'daily_open': opens,
        'daily_high': highs,
        'daily_low': lows,
        'daily_close': closes,
        'daily_volume': volumes
    })
    
    # Add metadata columns
    df['last_refreshed'] = last_refreshed
    df['Output Size'] = output_size
    df['Time Zone'] = time_zone
    df['Description'] = description
    df['symbol'] = symbol  
    
    return df
