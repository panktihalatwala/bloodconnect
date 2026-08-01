from django.shortcuts import render, redirect
from .forms import DonorForm, BloodRequestForm
from .utils import find_matching_donors

def register_donor(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('register_success')
    else:
        form = DonorForm()
    return render(request, 'donors/register.html', {'form': form})

def register_success(request):
    return render(request, 'donors/success.html')

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