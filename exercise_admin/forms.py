from django import forms
from english.models import COURSE, LESSON


class KhoaHocForm(forms.Form):
    course = forms.ModelChoiceField(
        queryset=COURSE.objects.all(),
        label='Khóa học',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class BuoiHocForm(forms.ModelForm):
    lesson_name = forms.ModelChoiceField(
        queryset=LESSON.objects.all(),
        label='Tên bài học',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

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
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập mô tả bài học'
            }),
            'lesson_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'exercise_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
        }
