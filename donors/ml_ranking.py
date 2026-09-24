"""
Integrates the ML baseline ranking model (ml/train_baseline_model.py) into
the live donor-matching flow, implementing FR-14 (rank matched donors by
predicted response likelihood).

Design decisions, documented here for the project report:

1. Cold-start handling via mean imputation: donors with no DonationHistory
   records and no last_donation_date cannot have real Recency/Frequency/
   Monetary/Time values computed (confirmed as the current state for all
   real donors during Week 11 verification). Rather than excluding these
   donors or unfairly penalizing them with a worst-case score, we impute
   the UCI training dataset's mean feature values. This is a standard,
   named technique in supervised learning (mean imputation) rather than an
   invented shortcut, and it avoids systematically demoting every donor
   simply because the project has not yet accumulated donation history.

2. Ranking is used only to ORDER matched donors, not to display a raw
   probability score to end users. The baseline model's precision (0.44)
   is not high enough to present as a trustworthy numeric confidence figure
   to non-technical users, so only the resulting order is exposed.

3. Fail-safe behavior: if the model file is missing or fails to load for
   any reason, donor matching still returns results in their original
   (unranked) order rather than breaking the core matching feature.
"""
import os
from datetime import date

FEATURE_COLUMNS = ["Recency (months)", "Frequency (times)", "Monetary (c.c. blood)", "Time (months)"]

# Mean feature values from the UCI training dataset (ml/transfusion_raw.csv),
# used as a neutral imputed default for donors with no recorded donation
# history, rather than assuming worst-case or best-case behavior.
TRAINING_MEAN_DEFAULTS = {
    "Recency (months)": 9.51,
    "Frequency (times)": 5.51,
    "Monetary (c.c. blood)": 1378.68,
    "Time (months)": 34.28,
}

STANDARD_DONATION_VOLUME_CC = 250

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'ml', 'donor_response_model.joblib'
)

_model_cache = None


def _load_model():
    global _model_cache
    if _model_cache is None:
        import joblib # noqa
        _model_cache = joblib.load(MODEL_PATH)
    return _model_cache


def _months_between(earlier_date, later_date):
    from dateutil.relativedelta import relativedelta # noqa
    if earlier_date is None:
        return None
    delta = relativedelta(later_date, earlier_date)
    return delta.years * 12 + delta.months


def compute_donor_features(donor, as_of_date=None):
    """
    Returns a dict of the four model features for a single Donor instance,
    using real DonationHistory data where available, falling back to the
    donor's last_donation_date for Recency only, and to training-set mean
    imputation for any feature that still cannot be computed.
    """
    if as_of_date is None:
        as_of_date = date.today()

    donations = list(donor.donationhistory_set.order_by('donation_date'))
    frequency = len(donations)

    if frequency > 0:
        earliest = donations[0].donation_date
        latest = donations[-1].donation_date
        recency = _months_between(latest, as_of_date)
        time_months = _months_between(earliest, as_of_date)
        monetary = frequency * STANDARD_DONATION_VOLUME_CC
    elif donor.last_donation_date:
        recency = _months_between(donor.last_donation_date, as_of_date)
        time_months = TRAINING_MEAN_DEFAULTS["Time (months)"]
        monetary = TRAINING_MEAN_DEFAULTS["Monetary (c.c. blood)"]
        frequency = TRAINING_MEAN_DEFAULTS["Frequency (times)"]
    else:
        recency = TRAINING_MEAN_DEFAULTS["Recency (months)"]
        time_months = TRAINING_MEAN_DEFAULTS["Time (months)"]
        monetary = TRAINING_MEAN_DEFAULTS["Monetary (c.c. blood)"]
        frequency = TRAINING_MEAN_DEFAULTS["Frequency (times)"]

    return {
        "Recency (months)": recency,
        "Frequency (times)": frequency,
        "Monetary (c.c. blood)": monetary,
        "Time (months)": time_months,
    }


def rank_donors_by_response_likelihood(donors):
    """
    donors: a list (or QuerySet) of Donor model instances.
    Returns a new list of the same donors, sorted from most to least likely
    to respond positively, based on the trained baseline model.
    Fails safe: if the model can't be loaded, returns donors unchanged
    rather than breaking the matching feature.
    """
    donors = list(donors)
    if not donors:
        return donors

    try:
        model = _load_model()
        import pandas as pd # noqa
        feature_rows = [compute_donor_features(d) for d in donors]
        X = pd.DataFrame(feature_rows)[FEATURE_COLUMNS]
        probabilities = model.predict_proba(X)[:, 1]
    except Exception:
        return donors

    ranked = sorted(zip(donors, probabilities), key=lambda pair: pair[1], reverse=True)
    return [donor for donor, _ in ranked]