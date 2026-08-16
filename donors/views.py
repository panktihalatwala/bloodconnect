from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import DonorForm, BloodRequestForm
from .utils import find_matching_donors_with_fallback
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Donor, BloodRequest, OTPVerification, MatchLog
from .email_utils import send_email_with_retry
from django.utils import timezone
import random

@login_required
def register_donor(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            donor = form.save(commit=False)
            donor.user = request.user
            donor.save()
            return redirect('register_success')
    else:
        form = DonorForm()
    return render(request, 'donors/register.html', {'form': form})

@login_required
def register_success(request):
    return render(request, 'donors/success.html')

@login_required
def submit_request(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.user = request.user
            blood_request.save()
            matches = find_matching_donors_with_fallback(blood_request.blood_group_needed, blood_request.hospital_location)
            for donor in matches:
                _, created = MatchLog.objects.get_or_create(donor=donor, blood_request=blood_request)
                if created:
                    plain_message = (
                        f"Dear {donor.name},\n\n"
                        f"You have been matched to a blood request for {blood_request.blood_group_needed} "
                        f"at {blood_request.hospital_location} (Urgency: {blood_request.urgency}).\n\n"
                        "Please log in to your BloodConnect donor dashboard to accept or decline this match.\n\n"
                        "Warm regards,\n"
                        "The BloodConnect Team"
                    )
                    html_message = f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; color: #333;">
                        <h2 style="color: #b30000;">BloodConnect</h2>
                        <p>Dear {donor.name},</p>
                        <p>You have been matched to a blood request:</p>
                        <ul>
                            <li><strong>Blood Group:</strong> {blood_request.blood_group_needed}</li>
                            <li><strong>Hospital:</strong> {blood_request.hospital_location}</li>
                            <li><strong>Urgency:</strong> {blood_request.urgency}</li>
                        </ul>
                        <p>Please log in to your BloodConnect donor dashboard to accept or decline this match.</p>
                        <p style="margin-top: 30px;">Warm regards,<br>
                        <strong>The BloodConnect Team</strong></p>
                        <hr style="border: none; border-top: 1px solid #ddd; margin-top: 20px;">
                        <p style="font-size: 12px; color: #888;">This is an automated message from BloodConnect. Please do not reply directly to this email.</p>
                    </div>
                    """
                    send_email_with_retry(
                        subject='You Have Been Matched — BloodConnect',
                        message=plain_message,
                        recipient_list=[donor.email],
                        html_message=html_message,
                    )
            return render(request, 'donors/results.html', {'matches': matches, 'request_obj': blood_request})
    else:
        form = BloodRequestForm()
    return render(request, 'donors/submit_request.html', {'form': form})

def home(request):
    return render(request, 'donors/home.html')

@role_required('admin')
def verify_donors_list(request):
    unverified = Donor.objects.filter(is_verified=False)
    return render(request, 'donors/verify_donors.html', {
        'donors': unverified,
        'pending_count': unverified.count(),
    })

@role_required('admin')
def verify_donor(request, donor_id):
    donor = Donor.objects.get(id=donor_id)
    donor.is_verified = True
    donor.save()

    plain_message = (
        f"Dear {donor.name},\n\n"
        "We are pleased to inform you that your donor profile with BloodConnect "
        "has been reviewed and successfully verified by our admin team.\n\n"
        "As a verified donor, you may now be contacted for emergency blood requests "
        "matching your blood group and availability.\n\n"
        "Thank you for registering as a blood donor and supporting your community.\n\n"
        "Warm regards,\n"
        "The BloodConnect Team"
    )

    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; color: #333;">
        <h2 style="color: #b30000;">BloodConnect</h2>
        <p>Dear {donor.name},</p>
        <p>We are pleased to inform you that your donor profile with <strong>BloodConnect</strong>
        has been reviewed and successfully <strong>verified</strong> by our admin team.</p>
        <p>As a verified donor, you may now be contacted for emergency blood requests matching
        your blood group and availability.</p>
        <p>Thank you for registering as a blood donor and supporting your community.</p>
        <p style="margin-top: 30px;">Warm regards,<br>
        <strong>The BloodConnect Team</strong></p>
        <hr style="border: none; border-top: 1px solid #ddd; margin-top: 20px;">
        <p style="font-size: 12px; color: #888;">This is an automated message from BloodConnect. Please do not reply directly to this email.</p>
    </div>
    """

    email_sent = send_email_with_retry(
        subject='You Are Now a Verified Donor — BloodConnect',
        message=plain_message,
        recipient_list=[donor.email],
        html_message=html_message,
    )

    if email_sent:
        messages.success(request, f"{donor.name} has been verified and notified by email.")
    else:
        messages.warning(request, f"{donor.name} has been verified, but the notification email failed to send. Check email_activity.log.")

    return redirect('verify_donors_list')

def send_otp(request, request_id):
    blood_request = BloodRequest.objects.get(id=request_id)
    otp_code = str(random.randint(100000, 999999))
    OTPVerification.objects.create(blood_request=blood_request, otp_code=otp_code)

    plain_message = (
        f"Dear {blood_request.requester_name},\n\n"
        "Thank you for using BloodConnect to search for blood donors.\n\n"
        f"Your One-Time Password (OTP) to view donor contact details is: {otp_code}\n\n"
        "This code is valid for a single verification and should not be shared with anyone.\n\n"
        "If you did not request this, please disregard this email.\n\n"
        "Warm regards,\n"
        "The BloodConnect Team"
    )

    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; color: #333;">
        <h2 style="color: #b30000;">BloodConnect</h2>
        <p>Dear {blood_request.requester_name},</p>
        <p>Thank you for using <strong>BloodConnect</strong> to search for blood donors.</p>
        <p>Your One-Time Password (OTP) to view donor contact details is:</p>
        <p style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #b30000; text-align: center; margin: 20px 0;">{otp_code}</p>
        <p>This code is valid for a single verification and should not be shared with anyone.</p>
        <p>If you did not request this, please disregard this email.</p>
        <p style="margin-top: 30px;">Warm regards,<br>
        <strong>The BloodConnect Team</strong></p>
        <hr style="border: none; border-top: 1px solid #ddd; margin-top: 20px;">
        <p style="font-size: 12px; color: #888;">This is an automated message from BloodConnect. Please do not reply directly to this email.</p>
    </div>
    """

    send_email_with_retry(
        subject='Your BloodConnect OTP Code',
        message=plain_message,
        recipient_list=[blood_request.requester_email],
        html_message=html_message,
    )
    return redirect('verify_otp', request_id=request_id)

def verify_otp(request, request_id):
    blood_request = BloodRequest.objects.get(id=request_id)
    error = None
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code')
        otp_record = OTPVerification.objects.filter(blood_request=blood_request, otp_code=entered_otp).last()
        if otp_record:
            otp_record.is_verified = True
            otp_record.save()
            matches = find_matching_donors_with_fallback(blood_request.blood_group_needed, blood_request.hospital_location)
            return render(request, 'donors/results.html', {'matches': matches, 'request_obj': blood_request, 'verified': True})
        else:
            error = "Invalid OTP. Please try again."
    return render(request, 'donors/verify_otp.html', {'request_obj': blood_request, 'error': error})

@role_required('donor')
def donor_dashboard(request):
    donor = get_object_or_404(Donor, user=request.user)
    pending_matches = MatchLog.objects.filter(donor=donor, status='Pending').select_related('blood_request')
    past_matches = MatchLog.objects.filter(donor=donor).exclude(status='Pending').select_related('blood_request')
    return render(request, 'donors/donor_dashboard.html', {
        'donor': donor,
        'pending_matches': pending_matches,
        'past_matches': past_matches,
    })

@role_required('donor')
def respond_to_match(request, match_id):
    donor = get_object_or_404(Donor, user=request.user)
    match = get_object_or_404(MatchLog, id=match_id, donor=donor)
    if request.method == 'POST':
        response = request.POST.get('response')
        if response in ('Accepted', 'Rejected'):
            match.status = response
            match.responded_at = timezone.now()
            match.save()
    return redirect('donor_dashboard')