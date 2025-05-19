from django import forms
from english.models import LESSON, LESSON_DETAIL, COURSE

class CombinedLessonForm(forms.Form):
    # Field từ LESSON
    lesson_file = forms.FileField(
        label="Tài liệu bài học (PDF)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
        required=False
    )
    exercise_file = forms.FileField(
        label="Tài liệu bài tập (PDF)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'application/pdf'}),
        required=False
    )
    course = forms.ModelChoiceField(
        label="Khóa học",
        queryset=COURSE.objects.none(),  # sẽ cập nhật trong __init__
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Các trường từ LESSON
    lesson_name = forms.CharField(
        label="Tên tài liệu",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên tài liệu'})
    )
    description = forms.CharField(
        label="Mô tả",
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Nhập mô tả tài liệu', 'rows': 4}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.lesson_instance = kwargs.pop('lesson_instance', None)
        super().__init__(*args, **kwargs)

        # Cập nhật danh sách khóa học
        self.fields['course'].queryset = COURSE.objects.all()

        # Set dữ liệu ban đầu nếu đang chỉnh sửa
        if self.lesson_instance:
            self.fields['course'].initial = self.lesson_instance.course
            self.fields['lesson_name'].initial = self.lesson_instance.lesson_name
            self.fields['description'].initial = self.lesson_instance.description

    def save(self):
        # Lưu dữ liệu vào LESSON
        lesson = self.lesson_instance or LESSON()
        lesson.course = self.cleaned_data['course']

        # Cập nhật tài liệu bài học nếu có
        if self.cleaned_data.get('lesson_file'):
            lesson.lesson_file = self.cleaned_data['lesson_file']

        # Cập nhật tài liệu bài tập nếu có
        if self.cleaned_data.get('exercise_file'):
            lesson.exercise_file = self.cleaned_data['exercise_file']

        # Cập nhật tên tài liệu và mô tả
        lesson.lesson_name = self.cleaned_data['lesson_name']
        lesson.description = self.cleaned_data['description']

        lesson.save()

        return lesson
