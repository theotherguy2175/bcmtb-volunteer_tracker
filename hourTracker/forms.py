from django import forms
from .models import VolunteerEntry

class VolunteerEntryForm(forms.ModelForm):
    class Meta:
        model = VolunteerEntry
        fields = ['date', 'hours', 'category']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
