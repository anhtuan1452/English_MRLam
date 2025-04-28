from django import forms
from english.models import EXERCISE, COURSE, LESSON


class KhoaHocForm(forms.ModelForm):
    class Meta:
        model = COURSE
        fields = ['course_name']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên khóa học'
            }),
        }
class BuoiHocForm(forms.ModelForm):
    class Meta:
        model = LESSON
        fields = ['lesson_file', 'exercise_file']
        widgets = {
            'lesson_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tải lên file bài học'
            }),
            'exercise_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tải lên file bài tập'
            }),
        }

