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

    # Field từ LESSON_DETAIL
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
        self.detail_instance = kwargs.pop('detail_instance', None)
        super().__init__(*args, **kwargs)

        # Cập nhật danh sách khóa học
        self.fields['course'].queryset = COURSE.objects.all()

        # Set dữ liệu ban đầu nếu đang chỉnh sửa
        if self.lesson_instance:
            self.fields['course'].initial = self.lesson_instance.course
        if self.detail_instance:
            self.fields['lesson_name'].initial = self.detail_instance.lesson_name
            self.fields['description'].initial = self.detail_instance.description

    def save(self):
        # Lưu dữ liệu vào LESSON
        lesson = self.lesson_instance or LESSON()
        lesson.course = self.cleaned_data['course']
        if self.cleaned_data.get('lesson_file'):
            lesson.lesson_file = self.cleaned_data['lesson_file']
        if self.cleaned_data.get('exercise_file'):
            lesson.exercise_file = self.cleaned_data['exercise_file']
        lesson.save()

        # Lưu dữ liệu vào LESSON_DETAIL
        detail = self.detail_instance or LESSON_DETAIL(lesson=lesson)
        detail.lesson_name = self.cleaned_data['lesson_name']
        detail.description = self.cleaned_data['description']
        detail.save()

        return lesson
