from datetime import date, timedelta
from .models import Donor

COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}

def get_compatible_donor_groups(blood_group_needed):
    compatible = []
    for donor_group, can_donate_to in COMPATIBILITY.items():
        if blood_group_needed in can_donate_to:
            compatible.append(donor_group)
    return compatible

def is_eligible(last_donation_date):
    if last_donation_date is None:
        return True
    return (date.today() - last_donation_date) > timedelta(days=90)

def find_matching_donors(blood_group_needed, location=None):
    compatible_groups = get_compatible_donor_groups(blood_group_needed)
    donors = Donor.objects.filter(
        blood_group__in=compatible_groups,
        availability_status=True
    )
    eligible_donors = [d for d in donors if is_eligible(d.last_donation_date)]
    if location:
        eligible_donors = [d for d in eligible_donors if location.lower() in d.location.lower()]
    return eligible_donors
