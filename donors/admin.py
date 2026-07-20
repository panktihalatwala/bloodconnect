from django.contrib import admin
from .models import Donor, BloodRequest, DonationHistory

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'location', 'availability_status', 'is_verified']

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['requester_name', 'blood_group_needed', 'urgency', 'status']

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'is_confirmed']