from django import forms
from english.models import Exercise

class BaiTapForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'

