from django import forms
from english.models import LESSON, COURSE

class CombinedLessonForm(forms.ModelForm):
    class Meta:
        model = LESSON
        fields = ['lesson_file', 'exercise_file', 'course', 'lesson_name', 'description']

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
        queryset=COURSE.objects.all(),  # Sử dụng queryset cho các khóa học
        widget=forms.Select(attrs={'class': 'form-control'})
    )
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

        # Nếu đang chỉnh sửa, set dữ liệu ban đầu
        if self.lesson_instance:
            self.fields['course'].initial = self.lesson_instance.course
            self.fields['lesson_name'].initial = self.lesson_instance.lesson_name
            self.fields['description'].initial = self.lesson_instance.description

    def save(self, commit=True):
        lesson = super().save(commit=False)  # Chưa lưu vào DB

        # Nếu có file lesson_file, gán vào lesson
        if self.cleaned_data.get('lesson_file'):
            lesson.lesson_file = self.cleaned_data['lesson_file']

        # Nếu có file exercise_file, gán vào lesson
        if self.cleaned_data.get('exercise_file'):
            lesson.exercise_file = self.cleaned_data['exercise_file']

        # Lưu tài liệu vào cơ sở dữ liệu
        if commit:
            lesson.save()

        return lesson
