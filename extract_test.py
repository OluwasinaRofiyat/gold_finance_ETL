import requests
import pytest

API_URL = "https://api.example.com/data"
EXPECTED_FIELDS = {"id", "name", "date", "value"}

def test_api_schema():
    response = requests.get(API_URL)
    assert response.status_code == 200
    data = response.json()
    assert EXPECTED_FIELDS.issubset(data[0].keys())

def test_sample_data():
    sample_data = {"id": 1, "name": "Sample", "date": "2023-01-01", "value": 123}
    response = requests.get(API_URL)
    assert sample_data in response.json()
