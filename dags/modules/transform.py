from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StructField, DateType, DoubleType, StringType, IntegerType
import os
 

def apply_data_quality_checks(df):
    """
    Applies data quality rules on the Spark DataFrame.

    Parameters:
        - df (DataFrame): The input Spark DataFrame.

    Returns:
        - (DataFrame, bool): Transformed DataFrame and a boolean flag if all checks pass.
    """

    # 1. Check for missing values in critical columns
    required_columns = ['date', 'daily_close', 'symbol']
    for col in required_columns:
        missing_count = df.filter(F.col(col).isNull()).count()
        if missing_count > 0:
            print(f"Data Quality Failed: {col} contains {missing_count} missing values.")
            return df, False

    # 2. Check for duplicate rows based on 'date' and 'symbol'
    duplicates = df.groupBy('date', 'symbol').count().filter(F.col('count') > 1).count()
    if duplicates > 0:
        print(f"Data Quality Failed: {duplicates} duplicate rows found.")
        return df, False

    # 3. Check for invalid ranges (daily_open, daily_close should be non-negative)
    invalid_ranges = df.filter((F.col("daily_close") < 0) | (F.col("daily_open") < 0)).count()
    if invalid_ranges > 0:
        print(f"Data Quality Failed: {invalid_ranges} rows have invalid price ranges.")
        return df, False

    # 4. Business Logic Validation: daily_close should be >= daily_low and <= daily_high
    invalid_business_logic = df.filter(
        (F.col("daily_close") < F.col("daily_low")) | (F.col("daily_close") > F.col("daily_high"))
    ).count()
    if invalid_business_logic > 0:
        print(f"Data Quality Failed: {invalid_business_logic} rows violate business logic.")
        return df, False

    print("All Data Quality Checks Passed!")
    return df, True



def transform_and_write_to_csv():
    """
    Transforms the input CSV file and writes it to the specified output path.
    """
    try:
        # Define schema
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
        #temp_dir = "/home/rita/Finance_ETL/myenv/dags/tmp/transformed_data/spark_temp"
        #os.makedirs(temp_dir, exist_ok=True)
        # Initialize Spark session
        spark = SparkSession.builder \
            .appName("Alpha Vantage Data Transformation") \
            .config("spark.local.dir", "/tmp/spark_temp") \
            .getOrCreate()

        # Read the CSV file as a Spark DataFrame
        input_path = "/tmp/alpha_vantage.csv"
        spark_df = spark.read.format("csv") \
            .option("header", True) \
            .schema(schema) \
            .load(input_path)

        if spark_df.count() == 0:
            print(f"No data found in {input_path}. Exiting.")
            return

        # Transformations
        spark_df = spark_df.withColumn("date", F.to_date("date")).orderBy("date")
        window_spec = Window.orderBy("date")
        spark_df = spark_df.withColumn(
            "daily_return",
            F.col("daily_close") - F.lag("daily_close", 1).over(window_spec)
        )

        # Ensure output directory exists
        output_transformed_path = "/tmp/spark_output"


        # Write the Spark DataFrame to CSV
        spark_df.write.format("csv").option("header", "true").mode("overwrite").save(output_transformed_path)
        print(f"Data successfully transformed and saved to {output_transformed_path}")

        # Show the transformed DataFrame (for testing purposes)
        spark_df.show()
    except Exception as e:
        print(f"An error occurred: {e}")