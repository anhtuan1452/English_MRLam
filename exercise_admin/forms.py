from django import forms
from english.models import COURSE, LESSON


class KhoaHocForm(forms.ModelForm):
    class Meta:
        model = COURSE
        fields = ['course_name']
        labels = {
            'course_name': 'Tên khóa học',
        }
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên khóa học'
            }),
        }
class BuoiHocForm(forms.ModelForm):
    class Meta:
        model = LESSON
        fields = ['lesson_name', 'description', 'lesson_file', 'exercise_file']
        labels = {
            'lesson_name': 'Tên bài học',
            'description': 'Mô tả',
            'lesson_file': 'File bài học',
            'exercise_file': 'File bài tập',
        }
        widgets = {
            'lesson_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên bài học'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mô tả bài học'
            }),
            'lesson_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tải lên file bài học'
            }),
            'exercise_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tải lên file bài tập'
            }),
        }

