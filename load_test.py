import pandas as pd
from sqlalchemy import create_engine
import pytest

engine = create_engine("postgresql+psycopg2://user:password@localhost/test_db")

def test_load_row_count():
    api_data = pd.read_json("sample_api_data.json")
    db_data = pd.read_sql("SELECT * FROM my_table", engine)
    assert len(api_data) == len(db_data)

def test_field_values():
    db_data = pd.read_sql("SELECT id, name, date, value FROM my_table LIMIT 10", engine)
    expected_data = pd.read_json("expected_data.json")
    pd.testing.assert_frame_equal(db_data, expected_data)
