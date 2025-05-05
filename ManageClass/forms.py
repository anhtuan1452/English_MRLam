from django import forms
from django.forms import modelformset_factory

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

from django import forms
from django.forms import modelformset_factory
from english.models import LESSON_DETAIL, LESSON, CLASS

# forms.py
from django import forms
from django.forms import modelformset_factory
from english.models import LESSON_DETAIL, LESSON, CLASS

from django import forms



class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        fields = ['lesson_name', 'description', 'session_number']

    lesson_name = forms.CharField(max_length=255, label='Tên buổi học')
    description = forms.CharField(widget=forms.Textarea, label='Mô tả')
    session_number = forms.IntegerField(min_value=1, label='Số buổi')
