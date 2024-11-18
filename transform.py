from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, DateType, DoubleType, StringType, IntegerType
import pandas as pd

def transform_and_write_to_csv(pandas_df, output_path):
    """
    Transforms the input pandas DataFrame and writes it to CSV as a Spark DataFrame.
    
    Parameters:
    - pandas_df (pd.DataFrame): Input pandas DataFrame with time series data.
    - output_path (str): Path to save the transformed Spark DataFrame in CSV format.
    """
    # Convert the 'date' column to datetime (DateType) in pandas DataFrame
    pandas_df['date'] = pd.to_datetime(pandas_df['date'])
    pandas_df['last_refreshed'] = pd.to_datetime(pandas_df['last_refreshed'])
    
    # Define the schema for the Spark DataFrame
    schema = StructType([
        StructField("date", DateType(), True),
        StructField("daily_open", DoubleType(), True),
        StructField("daily_high", DoubleType(), True),
        StructField("daily_low", DoubleType(), True),
        StructField("daily_close", DoubleType(), True),
        StructField("daily_volume", IntegerType(), True),
        StructField("last_refreshed", StringType(), True),
        StructField("output_size", StringType(), True),
        StructField("time_zone", StringType(), True),
        StructField("description", StringType(), True),
        StructField("symbol", StringType(), True)
    ])
    
    # Initialize Spark session
    spark = SparkSession.builder.appName("Alpha Vantage Data Transformation").getOrCreate()

    # Convert the pandas DataFrame to a Spark DataFrame using the defined schema
    spark_df = spark.createDataFrame(pandas_df, schema=schema)
    
    # Convert 'date' column to DateType and sort by date
    spark_df = spark_df.withColumn('date', F.to_date(F.col('date'))).orderBy('date')
    
    # Define a window specification for calculating daily return
    window_spec = Window.orderBy('date')
    
    # Calculate daily returns (difference in closing price)
    spark_df = spark_df.withColumn(
        'daily_return',
        F.col('daily_close') - F.lag('daily_close', 1).over(window_spec)
    )
    
    # Write the Spark DataFrame to CSV
    spark_df.write.csv(output_path, mode="overwrite", header=True)
    
    # Show the first few rows of the transformed DataFrame
    spark_df.show()

# Example usage
# Assuming `all_data_df` is the pandas DataFrame containing your data
df_combined = pd.read_csv('./landing_data/alpha_vantage.csv')

output_path = './data/alpha_vantage_transformed_data.csv'
transform_and_write_to_csv(df_combined, output_path)
