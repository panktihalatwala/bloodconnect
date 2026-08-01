from django import forms
from .models import Donor, BloodRequest

class DonorForm(forms.ModelForm):
    class Meta:
        model = Donor
        fields = ['name', 'email', 'blood_group', 'phone_number', 'location', 'availability_status', 'last_donation_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'availability_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'last_donation_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['requester_name', 'blood_group_needed', 'urgency', 'hospital_location']
        widgets = {
            'requester_name': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group_needed': forms.Select(attrs={'class': 'form-select'}),
            'urgency': forms.Select(attrs={'class': 'form-select'}),
            'hospital_location': forms.TextInput(attrs={'class': 'form-control'}),
        }