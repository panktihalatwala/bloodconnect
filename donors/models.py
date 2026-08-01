from django.db import models

class Donor(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

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

    requester_name = models.CharField(max_length=100)
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