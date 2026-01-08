
from django import forms
from hourTracker.models import CustomUser

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'address_line_1', 'address_line_2', 'city', 'state', 'zip_code'] # Add any other fields here