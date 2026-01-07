from django import forms
from .models import VolunteerEntry, CustomUser

class VolunteerEntryForm(forms.ModelForm):
    class Meta:
        model = VolunteerEntry
        fields = ['date', 'hours', 'category', 'location']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        pass


from django.contrib.auth import get_user_model # Add this import
# Get the active user model (which is your CustomUser)
User = get_user_model()
class AdminVolunteerEntryForm(VolunteerEntryForm):
    # This is the visible search box
    user_search = forms.CharField(
        label="Volunteer Name",
        widget=forms.TextInput(attrs={
            'placeholder': 'Type to search volunteers...',
            'class': 'input', # Bulma/Bootstrap style
            'autocomplete': 'off'
        })
    )
    # This stores the ID so Django can save the entry
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.HiddenInput()
    )

    class Meta(VolunteerEntryForm.Meta):
        fields = ['user_search', 'user'] + VolunteerEntryForm.Meta.fields


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
        fields = ("email", "first_name", "last_name", "phone_number")

