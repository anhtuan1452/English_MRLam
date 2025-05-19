from django import forms
from english.models import CLASS, LESSON_DETAIL,LESSON

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

class LessonForm(forms.ModelForm):
    class Meta:
        model = LESSON
        fields = ['lesson_name', 'session_number', 'description']
        widgets = {
            'lesson_name': forms.TextInput(attrs={'class': 'form-control'}),
            'session_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }