import requests
import pytest

# Define the API URL template
def fetch_api_data(symbol: str, api_key: str) -> dict:
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    response = requests.get(url)
    
    # Validate the response status
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
    
    # Ensure the response contains the expected structure
    data = response.json()
    
    # Validate the response contains 'Time Series (Daily)'
    if "Time Series (Daily)" not in data:
        raise KeyError(f"Expected key 'Time Series (Daily)' not found in response.")
    
    return data

# Define a function to log the test results or raise errors
def validate_api_response(symbol: str, api_key: str):
    try:
        data = fetch_api_data(symbol, api_key)
        # You can add further checks here (e.g., data format, number of entries, etc.)
        print(f"API Response for {symbol}: Data fetched successfully.")
        
    except (ValueError, KeyError) as error:
        print(f"API Test failed for {symbol}: {error}")
        raise error