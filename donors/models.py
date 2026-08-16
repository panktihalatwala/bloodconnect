from django.db import models
from django.contrib.auth.models import User

class Donor(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='donor_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    availability_status = models.BooleanField(default=True)
    last_donation_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.blood_group})"


class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ('High', 'High'), ('Medium', 'Medium'), ('Low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'), ('Fulfilled', 'Fulfilled'), ('Expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='blood_requests')
    requester_name = models.CharField(max_length=100)
    requester_email = models.EmailField(max_length=254, default='')
    blood_group_needed = models.CharField(max_length=3, choices=Donor.BLOOD_GROUP_CHOICES)
    urgency = models.CharField(max_length=10, choices=URGENCY_CHOICES)
    hospital_location = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request by {self.requester_name} for {self.blood_group_needed}"


class DonationHistory(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.SET_NULL, null=True, blank=True)
    donation_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.donor.name} - {self.donation_date}"


class OTPVerification(models.Model):
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class MatchLog(models.Model):
    RESPONSE_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='match_logs')
    blood_request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='match_logs')
    status = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default='Pending')
    matched_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('donor', 'blood_request')

    def __str__(self):
        return f"{self.donor.name} -> {self.blood_request} [{self.status}]"