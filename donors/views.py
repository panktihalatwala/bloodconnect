from django.shortcuts import render, redirect
from .forms import DonorForm, BloodRequestForm
from .utils import find_matching_donors
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Donor

@login_required
def register_donor(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
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
            blood_request = form.save()
            matches = find_matching_donors(blood_request.blood_group_needed, blood_request.hospital_location)
            return render(request, 'donors/results.html', {'matches': matches, 'request_obj': blood_request})
    else:
        form = BloodRequestForm()
    return render(request, 'donors/submit_request.html', {'form': form})
def home(request):
    return render(request, 'donors/home.html')

@role_required('admin')
def verify_donors_list(request):
    unverified = Donor.objects.filter(is_verified=False)
    return render(request, 'donors/verify_donors.html', {'donors': unverified})

from django.core.mail import send_mail

@role_required('admin')
def verify_donor(request, donor_id):
    donor = Donor.objects.get(id=donor_id)
    donor.is_verified = True
    donor.save()
    send_mail(
        subject='You are now a verified donor — BloodConnect',
        message=f'Hi {donor.name}, your donor profile has been verified by our admin team. You may now be contacted for emergency blood requests.',
        from_email='bloodconnect@example.com',
        recipient_list=[donor.email],
        fail_silently=False,
    )
    return redirect('verify_donors_list')