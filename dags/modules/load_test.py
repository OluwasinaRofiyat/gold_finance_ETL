#from airflow.hooks.postgres_hook import PostgresHook

def test_postgres_connection():
    """
    Test the connection to PostgreSQL using PostgresHook.
    """
    try:
        # Replace 'my_postgres_conn_id' with your Airflow connection ID
        postgres_hook = PostgresHook(postgres_conn_id="on_prem_postgres")
        connection = postgres_hook.get_conn()
        cursor = connection.cursor()

        # Simple query to verify the connection
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        
        assert result == (1,), "Postgres connection test failed!"
        print("Postgres connection test passed.")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"Error testing PostgresHook connection: {e}")

