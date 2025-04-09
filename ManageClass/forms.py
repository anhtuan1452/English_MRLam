from django import forms
from english.models import Class

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['class_name', 'course', 'begin_time', 'end_time']
