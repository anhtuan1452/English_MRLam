from django import forms
from english.models import CLASS


class ClassForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time', 'status', 'timetable']
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên lớp học'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'begin_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_time': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'timetable': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
