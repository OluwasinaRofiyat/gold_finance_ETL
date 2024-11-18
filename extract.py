import requests
import pandas as pd
import psycopg2
from psycopg2 import sql
import os

from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, IntegerType, StructField, StringType, DoubleType, DateType

# Function to get the max date from the PostgreSQL staging table
def get_max_date_from_staging(connection_string, table_name):
    """Fetch the maximum date from the staging table in PostgreSQL"""
    query = f"SELECT MAX(date) FROM {table_name};"
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(query)
        max_date = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        # If max_date is None, return a default old date (e.g., 2000-01-01)
        return max_date if max_date else datetime(2000, 1, 1)
    
    except Exception as e:
        print(f"Error fetching max date: {e}")
        return datetime(2000, 1, 1)

def fetch_alpha_vantage_data(symbol, api_key, max_date_from_db,**kwargs):
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
    last_refreshed = meta_data.get('3. Last Refreshed', '')
    
    # Initializing empty lists for time series data
    dates = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    
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
    df['symbol'] = symbol  
    
    return df


# Define your PostgreSQL connection string
connection_string = "postgresql://username:password@hostname:port/database_name"

# Define the table name in the staging area
table_name = "alpha_vantage.staging_finance_data"

# Get the maximum date from the PostgreSQL staging table
max_date_from_db = get_max_date_from_staging(connection_string, table_name)

# Define the list of symbols and your API key
symbols = ['TSCO.LON', 'IBM', 'MBG.DEX', 'SHOP.TRT']
api_key = "ML7BZYF38ZPZLHR4"

# Empty list to collect all dataframes
df_list = []

# Looping through the symbols and fetching data for each
for symbol in symbols:
    df_symbol = fetch_alpha_vantage_data(symbol, api_key, max_date_from_db)
    df_list.append(df_symbol)

# Concatenate all dataframes into one
df_combined = pd.concat(df_list, ignore_index=True)

# Display the first few rows of the combined dataframe
print(df_combined.head())



# Save the combined dataframe to CSV
df_combined.to_csv('./landing_data/alpha_vantage.csv', index=False)
