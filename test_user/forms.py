from django.forms import forms
from english.models import Test

class BaiTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = '__all__'