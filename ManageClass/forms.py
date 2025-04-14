from django import forms
from english.models import CLASS

class ClassForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time']
