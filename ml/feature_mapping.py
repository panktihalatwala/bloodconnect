"""
Maps the project's own Donor/DonationHistory data onto the same feature
structure used by the UCI Blood Transfusion dataset (Recency, Frequency,
Monetary, Time), so the trained model can eventually be applied to real
donors instead of only the UCI reference data or hand-typed samples.

This is groundwork only — it does not yet wire into the live matching
flow (donors/views.py); it proves the mapping is computable from our
actual schema.
"""
from datetime import date
from dateutil.relativedelta import relativedelta


STANDARD_DONATION_VOLUME_CC = 250  # matches the UCI dataset's assumed unit per donation


def months_between(earlier_date, later_date):
    """Whole months between two dates, UCI-dataset style (rounded down)."""
    if earlier_date is None:
        return None
    delta = relativedelta(later_date, earlier_date)
    return delta.years * 12 + delta.months


def extract_features_for_donor(donor, donation_history_queryset, as_of_date=None):
    """
    donor: a Donor model instance
    donation_history_queryset: DonationHistory records for this donor
    as_of_date: the reference date to compute Recency/Time from (defaults to today)

    Returns a dict with the four UCI-equivalent features, or None values
    for any feature that can't be computed from currently available data.
    """
    if as_of_date is None:
        as_of_date = date.today()

    donations = list(donation_history_queryset.order_by('donation_date'))
    frequency = len(donations)

    if frequency > 0:
        earliest_donation = donations[0].donation_date
        latest_donation = donations[-1].donation_date
        time_months = months_between(earliest_donation, as_of_date)
        recency_months = months_between(latest_donation, as_of_date)
    elif donor.last_donation_date:
        # Fallback: no DonationHistory records yet, but the Donor model itself
        # has a last_donation_date field from registration — use that as a
        # rough proxy for Recency, though Frequency/Time can't be derived from it alone.
        recency_months = months_between(donor.last_donation_date, as_of_date)
        time_months = None
    else:
        recency_months = None
        time_months = None

    monetary_cc = frequency * STANDARD_DONATION_VOLUME_CC

    return {
        "donor_id": donor.id,
        "donor_name": donor.name,
        "Recency (months)": recency_months,
        "Frequency (times)": frequency,
        "Monetary (c.c. blood)": monetary_cc,
        "Time (months)": time_months,
    }


if __name__ == "__main__":
    import os
    import sys
    import django

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloodconnect.settings')
    django.setup()

    from donors.models import Donor, DonationHistory

    print("=" * 70)
    print("FEATURE MAPPING: Donor/DonationHistory -> UCI-equivalent features")
    print("=" * 70)

    for donor in Donor.objects.all():
        history = DonationHistory.objects.filter(donor=donor)
        features = extract_features_for_donor(donor, history)
        print(features)