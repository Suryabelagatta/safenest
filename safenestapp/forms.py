from django import forms
from .models import MissingChild

class MissingChildForm(forms.ModelForm):
    class Meta:
        model = MissingChild
        fields = ['name', 'age', 'last_seen_date', 'last_seen_location', 'additional_info', 'photo', 'status']
