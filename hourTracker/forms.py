from django import forms
from .models import VolunteerEntry

class VolunteerEntryForm(forms.ModelForm):
    class Meta:
        model = VolunteerEntry
        fields = ['date', 'hours', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()


# class RegisterForm(forms.ModelForm):
#     first_name = forms.CharField(required=True)
#     last_name = forms.CharField(required=True)
#     password = forms.CharField(widget=forms.PasswordInput)
#     confirm_password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = User
#         fields = ['email', 'first_name', 'last_name', 'password']

#     def clean(self):
#         cleaned_data = super().clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")
#         if password != confirm_password:
#             raise forms.ValidationError("Passwords do not match")

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("email", "first_name", "last_name", "password1", "password2")

# #EDIT FORM LATER
# class CustomUserChangeForm(forms.ModelForm):
#     class Meta:
#         model = CustomUser
#         fields = ("email", "first_name", "last_name", "is_active", "is_staff")
