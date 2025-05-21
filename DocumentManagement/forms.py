
from django import forms
from english.models import DOCUMENT

class DocumentForm(forms.ModelForm):
    class Meta:
        model = DOCUMENT
        fields = ['doc_name', 'doc_file']
