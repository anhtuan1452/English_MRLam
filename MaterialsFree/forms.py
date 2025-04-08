# MaterialsFree/forms.py
from django import forms

class DocumentSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search here...',
        })
    )