from django import forms
from english.models import CLASS, LESSON_DETAIL

class ClassUpdateForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time', 'status', 'timetable']
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'begin_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'timetable': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        exclude = ['lesson']
        widgets = {
            'session_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'lesson_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
