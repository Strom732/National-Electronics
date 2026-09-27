from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

class ProfileSetupForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address','gst_no', 'gender', 'profile_image']
        widgets = {
            'gender': forms.Select(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]),
        }
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance

class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']  # Include fields you want to update

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom logic for form initialization if needed
