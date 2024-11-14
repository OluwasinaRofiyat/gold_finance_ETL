# Gold_finance_ETL
Overview
Gold_finance_ETL is a data engineering project designed to extract financial time series data from the Alpha Vantage API, transform it using PySpark, and load it into a PostgreSQL database. The pipeline is orchestrated with Apache Airflow, enabling automated and scheduled ETL tasks. Aggregated tables in PostgreSQL provide data for financial analysis, allowing users to generate insights into daily financial trends.

## Data Source
The pipeline pulls daily time series data from the Alpha Vantage API, specifically focusing on open, close, high, low prices, and volume. The API provides reliable and well-structured financial data suitable for aggregation and analysis.

API Endpoint: https://www.alphavantage.co/query?function=TIME_SERIES_DAILY
Frequency: Daily data refreshes
## Technologies
### Apache Airflow: Used for orchestration and scheduling
### PySpark: Employed for ETL transformations to handle and process data efficiently
### PostgreSQL: Database to store raw and aggregated tables with custom stored procedures for financial analysis
### SQL: Used for creating tables, views, and procedures for data aggregation
### Python: Core language for scripting and data manipulation
## Pipeline Workflow
Extract:
Using extract.py, the pipeline fetches daily time series data from the Alpha Vantage API.
Load:
Transformed data is loaded into PostgreSQL tables using load.py.
Aggregation:
aggregate tables are created in postgress to using stored SQLprocedures
Aggregated tables are generated in PostgreSQL using stored procedures and SQL scripts in stored_procedures.sql.
