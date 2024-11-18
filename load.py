from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, lit
from sqlalchemy import create_engine
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a PostgreSQL engine
def get_engine():
    return create_engine(
        'postgresql://{user}:{password}@{host}:{port}/{database}'.format(
            user=os.getenv('PG_USER'),
            password=os.getenv('PG_PASSWORD'),
            host=os.getenv('PG_HOST'),
            port=os.getenv('PG_PORT'),
            database=os.getenv('PG_DATABASE')
        )
    )

# Fetch the last loaded date
def get_last_loaded_date():
    print("Fetching last loaded date...")
    engine = get_engine()
    query = "SELECT MAX(date) FROM daily_finance;"
    result = engine.execute(query).fetchone()
    print("Last loaded date:", result[0])
    return result[0] if result[0] else None

# Load data into PostgreSQL
def load_data_to_postgres(data):
    # Create Spark session
    print("Initializing Spark session...")
    spark = SparkSession.builder.master("local[*]").appName("ETL Pipeline").getOrCreate()

    # Convert list of dictionaries to Spark DataFrame
    print("Converting data to Spark DataFrame...")
    df = spark.createDataFrame(data)

    # Ensure 'date' column is in date format
    print("Ensuring 'date' column is in date format...")
    df = df.withColumn('date', to_date(col('date')))

    # Get the last loaded date from PostgreSQL
    last_loaded_date = get_last_loaded_date()

    # Filter for new data
    print("Filtering for new data...")
    if last_loaded_date:
        last_loaded_date = datetime.strptime(str(last_loaded_date), '%Y-%m-%d').date()
        new_data = df.filter(col('date') > lit(last_loaded_date))
    else:
        new_data = df

    # Write new data to PostgreSQL
    if new_data.count() > 0:
        print("New data detected. Loading to PostgreSQL...")
        jdbc_url = f"jdbc:postgresql://{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
        connection_properties = {
            "user": os.getenv('PG_USER'),
            "password": os.getenv('PG_PASSWORD'),
            "driver": "org.postgresql.Driver"
        }
        new_data.write.jdbc(url=jdbc_url, table="daily_finance", mode="append", properties=connection_properties)
        print("Data successfully loaded to the database.")
    else:
        print("No new data to load.")
