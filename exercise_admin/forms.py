
from django import forms
from english.models import CLASS, LESSON_DETAIL

class ExerciseForm(forms.Form):
    class_selected = forms.ModelChoiceField(
        queryset=CLASS.objects.all(),
        label="Chọn lớp",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    session_number = forms.CharField(
        label="Buổi học",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    lesson_name = forms.CharField(
        label="Tên bài học",
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label="Mô tả buổi học",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    date = forms.DateField(
        label="Hạn nộp",
        required=True,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    lesson_file = forms.FileField(
        label="File bài học",
        required=False,
        widget=forms.ClearableFileInput()
    )
    exercise_file = forms.FileField(
        label="File bài tập",
        required=False,
        widget=forms.ClearableFileInput()
    )

    def __init__(self, *args, **kwargs):
        # Nhận thêm tham số lesson_detail_id để biết buổi học hiện tại đang sửa
        self.lesson_detail_id = kwargs.pop('lesson_detail_id', None)
        super().__init__(*args, **kwargs)

    def clean_session_number(self):
        session_number = self.cleaned_data['session_number']
        class_selected = self.cleaned_data.get('class_selected')

        if class_selected:
            # Lấy queryset buổi học cùng lớp và session_number
            qs = LESSON_DETAIL.objects.filter(
                classes=class_selected,
                lesson__session_number=session_number
            )
            if self.lesson_detail_id:
                # Loại trừ buổi đang sửa khỏi kiểm tra trùng
                qs = qs.exclude(pk=self.lesson_detail_id)
            if qs.exists():
                raise forms.ValidationError("Buổi học này đã tồn tại trong lớp được chọn.")
        return session_number