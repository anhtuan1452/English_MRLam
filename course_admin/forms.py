# course_admin/forms.py
from django import forms
from django.contrib.auth import get_user_model
from english.models import COURSE, CLASS, LESSON_DETAIL, LESSON

User = get_user_model()

class CourseForm(forms.ModelForm):
    teacher_name = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True, is_superuser=False),
        label="Giáo viên",
        empty_label="-- Chọn giáo viên --"
    )

    class Meta:
        model = COURSE
        fields = ['course_name', 'description', 'price', 'teacher_name', 'des_teacher']
        labels = {
            'course_name': 'Tên khóa học',
            'description': 'Mô tả',
            'price': 'Giá (VND)',
            'des_teacher': 'Mô tả giáo viên',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # override label_from_instance để hiển thị full name
        self.fields['teacher_name'].label_from_instance = lambda user: user.get_full_name() or user.username

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None or price < 0:
            raise forms.ValidationError("Giá phải là số ≥ 0")
        return price

    def save(self, commit=True):
        course = super().save(commit=False)
        teacher = self.cleaned_data['teacher_name']
        course.teacher_name = teacher.get_full_name() or teacher.username
        if commit:
            course.save()
        return course

class LessonForm(forms.ModelForm):
    lesson_name = forms.CharField(
        max_length=100,
        label='Chủ đề',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    description = forms.CharField(
        label='Mô tả',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=True
    )

    session_number = forms.CharField(
        label='Buổi học',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = LESSON
        fields = ['lesson_name', 'description', 'session_number']  # các trường chính của LESSON
from django.forms import modelformset_factory
class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        fields = ['date']  # Chỉ giữ trường date, vì session_number thuộc về LESSON
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    fields=['date'],
    extra=1
)