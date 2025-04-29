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

class LessonAndDetailForm(forms.Form):
    lesson_name = forms.CharField(
        max_length=100,
        label='Chủ đề',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ví dụ: Ngữ pháp cơ bản'})
    )
    description = forms.CharField(
        required=False,
        label='Mô tả',
        widget=forms.Textarea(attrs={'class':'form-control', 'rows':4, 'placeholder':'Mô tả ngắn'})
    )
    session_number = forms.CharField(
        max_length=100,
        label='Buổi',
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Ví dụ: Buổi 1'})
    )

    def __init__(self, *args, **kwargs):
        course = kwargs.pop('course', None)
        super().__init__(*args, **kwargs)
        if course:
            # Chỉ hiển thị các lớp thuộc khóa học
            self.fields['classes'].queryset = CLASS.objects.filter(course=course)


class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        fields = ['lesson_name', 'description', 'session_number']  # Cập nhật các trường dữ liệu bạn muốn

    lesson_name = forms.CharField(
        max_length=100,
        label='Chủ đề',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        required=False,
        label='Mô tả',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

    session_number = forms.CharField(
        label='Buổi',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Kiểm tra nếu object LESSON_DETAIL đã được tạo
            self.fields['lesson_name'] = forms.CharField(
                initial=self.instance.lesson.lesson_name if self.instance.lesson else '',
                label='Chủ đề',
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                required=False
            )
            self.fields['description'] = forms.CharField(
                initial=self.instance.lesson.description if self.instance.lesson else '',
                required=False,
                label='Mô tả',
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
            )
        else:
            # Nếu chưa lưu, bạn có thể để các giá trị mặc định
            self.fields['lesson_name'] = forms.CharField(
                required=False,
                label='Chủ đề',
                widget=forms.TextInput(attrs={'class': 'form-control'})
            )
            self.fields['description'] = forms.CharField(
                required=False,
                label='Mô tả',
                widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
            )