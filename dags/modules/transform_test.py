from unittest.mock import patch, MagicMock
#import pytest
from pyspark.sql import SparkSession
from modules.transform import transform_and_write_to_csv

def test_data_transformation():
    """
    Test the `transform_and_write_to_csv` function using mocks.
    """
    # Mock Spark Session, DataFrame, and transformations
    with patch('modules.transform.SparkSession') as mock_spark_session_class:
        # Mock Spark session and its DataFrame methods
        mock_spark = MagicMock()
        mock_spark_session_class.builder.getOrCreate.return_value = mock_spark

        mock_df = MagicMock()  # Mock Spark DataFrame
        mock_spark.read.format.return_value.option.return_value.schema.return_value.load.return_value = mock_df

        # Mock transformations
        mock_df.withColumn.return_value = mock_df
        mock_df.orderBy.return_value = mock_df

        # Mock Pandas DataFrame conversion and CSV writing
        mock_pandas_df = MagicMock()
        mock_df.toPandas.return_value = mock_pandas_df
        mock_pandas_df.to_csv = MagicMock()

        # Call the transformation function
        transform_and_write_to_csv()

        # Validate Spark DataFrame read
        mock_spark.read.format.assert_called_once_with("csv")
        mock_spark.read.format().option.assert_called_once_with("header", True)
        mock_spark.read.format().option().schema.assert_called()

        # Validate Spark DataFrame transformations
        mock_df.withColumn.assert_called()  # Check `withColumn` invocation
        mock_df.orderBy.assert_called_once_with("date")

        # Validate Pandas `to_csv` call
        mock_df.toPandas.assert_called_once()
        mock_pandas_df.to_csv.assert_called_once_with(
            '/opt/airflow/dags/alpha_vantage_transformed.csv', index=False
        )

        print("Test passed!")
