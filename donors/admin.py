from django.contrib import admin
from .models import Donor, BloodRequest, DonationHistory, OTPVerification, MatchLog

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['name', 'blood_group', 'location', 'availability_status', 'is_verified']

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['requester_name', 'blood_group_needed', 'urgency', 'status']

@admin.register(DonationHistory)
class DonationHistoryAdmin(admin.ModelAdmin):
    list_display = ['donor', 'donation_date', 'is_confirmed']

@admin.register(OTPVerification)
class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['blood_request', 'otp_code', 'is_verified', 'created_at']

@admin.register(MatchLog)
class MatchLogAdmin(admin.ModelAdmin):
    list_display = ['donor', 'blood_request', 'status', 'matched_at', 'responded_at']