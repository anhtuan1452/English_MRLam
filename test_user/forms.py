from django.forms import forms
from english.models import TEST

class BaiTestForm(forms.ModelForm):
    class Meta:
        model = TEST
        fields = '__all__'