"""
Step 3 of ML groundwork: use the trained baseline model to rank a list of
donors by predicted response likelihood, rather than just classifying
donate/won't-donate. This is the actual capability the matching engine
needs (FR-14: rank matched donors by predicted response likelihood).
"""
import joblib
import pandas as pd

MODEL_PATH = "ml/donor_response_model.joblib"

FEATURE_COLUMNS = ["Recency (months)", "Frequency (times)", "Monetary (c.c. blood)", "Time (months)"]


def load_model():
    return joblib.load(MODEL_PATH)


def rank_donors(donor_features_df):
    """
    donor_features_df: a DataFrame with columns matching FEATURE_COLUMNS,
    one row per candidate donor, indexed however the caller likes (e.g.
    by donor_id).

    Returns the same DataFrame with an added 'response_probability' column,
    sorted from most to least likely to respond.
    """
    model = load_model()
    probabilities = model.predict_proba(donor_features_df[FEATURE_COLUMNS])[:, 1]
    donor_features_df = donor_features_df.copy()
    donor_features_df["response_probability"] = probabilities
    return donor_features_df.sort_values("response_probability", ascending=False)


if __name__ == "__main__":
    # Example: simulate 3 candidate donors with made-up feature values,
    # just to prove the ranking logic works end-to-end before we wire in
    # real data from our own Donor/DonationHistory models.
    sample_donors = pd.DataFrame({
        "donor_name": ["Rahul Shah", "Priya Mehta", "Arjun Patel"],
        "Recency (months)": [1, 20, 5],
        "Frequency (times)": [8, 1, 3],
        "Monetary (c.c. blood)": [2000, 250, 750],
        "Time (months)": [40, 20, 15],
    })

    ranked = rank_donors(sample_donors)
    print("DONORS RANKED BY PREDICTED RESPONSE LIKELIHOOD:")
    print(ranked[["donor_name", "response_probability"]].to_string(index=False))