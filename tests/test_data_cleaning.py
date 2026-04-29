import os
import sys

import pandas as pd

# ensure src is importable as package
sys.path.insert(0, os.path.abspath("."))


def test_clean_data_splits_labels():
    from nourisher.ml.data_cleaning.dataframe import clean_data

    df = pd.DataFrame(
        [
            {"pcos": 0, "weight_kg": 60.0, "blood_11": 1},
            {"pcos": 1, "weight_kg": 70.0, "blood_12": 2},
        ]
    )

    cleaned, labels = clean_data(df)
    assert "pcos" not in cleaned.columns
    assert "blood_11" not in cleaned.columns
    assert "blood_12" not in cleaned.columns
    assert labels.tolist() == [0, 1]
