"""
Integration tests for the ML groundwork pipeline (dataset loading, model
training, and donor ranking). These are standalone tests (not Django
TestCase-based) since the ML pipeline currently operates independently
of the Django app, using pandas/scikit-learn directly.

Run with: python -m pytest ml/test_pipeline.py
or:       python -m unittest ml.test_pipeline
"""
import unittest
import os
import pandas as pd
import joblib

from ml.explore_dataset import load_dataset
from ml.train_baseline_model import (
    load_data, prepare_features, FEATURE_COLUMNS, TARGET_COLUMN, MODEL_OUTPUT_PATH
)
from ml.rank_donors import rank_donors, load_model


class DatasetTests(unittest.TestCase):

    def test_dataset_has_expected_shape(self):
        """The UCI dataset should always load with 748 rows and 5 columns."""
        df = load_dataset()
        self.assertEqual(df.shape, (748, 5))

    def test_dataset_has_no_missing_values(self):
        """The dataset should be complete, with no null/NaN cells."""
        df = load_dataset()
        self.assertEqual(df.isnull().sum().sum(), 0)

    def test_target_column_is_binary(self):
        """The target column should only contain 0 and 1."""
        df = load_dataset()
        target_col = df.columns[-1]
        unique_values = set(df[target_col].unique())
        self.assertEqual(unique_values, {0, 1})


class ModelFileTests(unittest.TestCase):

    def test_model_file_exists(self):
        """The trained model file should exist after training."""
        self.assertTrue(os.path.exists(MODEL_OUTPUT_PATH))

    def test_model_loads_without_error(self):
        """The saved model should load cleanly via joblib."""
        model = joblib.load(MODEL_OUTPUT_PATH)
        self.assertIsNotNone(model)

    def test_model_predicts_expected_shape(self):
        """The model should output one probability per input row."""
        model = joblib.load(MODEL_OUTPUT_PATH)
        sample = pd.DataFrame({
            "Recency (months)": [1, 20],
            "Frequency (times)": [8, 1],
            "Monetary (c.c. blood)": [2000, 250],
            "Time (months)": [40, 20],
        })
        probabilities = model.predict_proba(sample)
        self.assertEqual(probabilities.shape, (2, 2))  # 2 rows, 2 classes


class RankingTests(unittest.TestCase):

    def test_rank_donors_returns_sorted_output(self):
        """rank_donors should return donors sorted from highest to lowest probability."""
        sample_donors = pd.DataFrame({
            "donor_name": ["Frequent Donor", "Rare Donor"],
            "Recency (months)": [1, 30],
            "Frequency (times)": [10, 1],
            "Monetary (c.c. blood)": [2500, 250],
            "Time (months)": [50, 10],
        })
        ranked = rank_donors(sample_donors)

        self.assertEqual(len(ranked), 2)
        probabilities = ranked["response_probability"].tolist()
        self.assertEqual(probabilities, sorted(probabilities, reverse=True))

    def test_rank_donors_adds_probability_column(self):
        """rank_donors should add a response_probability column with valid probability values."""
        sample_donors = pd.DataFrame({
            "donor_name": ["Test Donor"],
            "Recency (months)": [5],
            "Frequency (times)": [3],
            "Monetary (c.c. blood)": [750],
            "Time (months)": [20],
        })
        ranked = rank_donors(sample_donors)

        self.assertIn("response_probability", ranked.columns)
        prob = ranked["response_probability"].iloc[0]
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)

    def test_frequent_recent_donor_ranks_above_rare_donor(self):
        """A frequent, recent donor should be ranked as more likely to respond
        than an infrequent, less recent donor — sanity check on model behavior."""
        sample_donors = pd.DataFrame({
            "donor_name": ["Frequent Donor", "Rare Donor"],
            "Recency (months)": [1, 30],
            "Frequency (times)": [10, 1],
            "Monetary (c.c. blood)": [2500, 250],
            "Time (months)": [50, 10],
        })
        ranked = rank_donors(sample_donors)

        top_donor = ranked.iloc[0]["donor_name"]
        self.assertEqual(top_donor, "Frequent Donor")


if __name__ == "__main__":
    unittest.main()