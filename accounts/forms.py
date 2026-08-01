from django import forms
from django.contrib.auth.models import User

class SignUpForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    is_donor = forms.BooleanField(required=False, label="I want to register as a donor")
    is_requester = forms.BooleanField(required=False, label="I want to be able to request blood")

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        if not cleaned_data.get('is_donor') and not cleaned_data.get('is_requester'):
            raise forms.ValidationError("Please select at least one: donor or requester.")
        return cleaned_data