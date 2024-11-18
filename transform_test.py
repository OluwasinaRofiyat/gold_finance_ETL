import pandas as pd
import pytest

def test_transformations():
    input_data = pd.DataFrame({"id": [1, 2], "date": ["2023-01-01", None]})
    expected_data = pd.DataFrame({"id": [1, 2], "date": ["2023-01-01", "N/A"]})
    transformed_data = my_transformation_function(input_data)
    pd.testing.assert_frame_equal(transformed_data, expected_data)
