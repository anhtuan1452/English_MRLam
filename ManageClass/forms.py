# from django import forms
# from english.models import CLASS, LESSON_DETAIL,LESSON
#
# class ClassUpdateForm(forms.ModelForm):
#     class Meta:
#         model = CLASS
#         fields = ['class_name', 'course', 'begin_time', 'end_time', 'status', 'timetable']
#         widgets = {
#             'class_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'begin_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'end_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'status': forms.Select(attrs={'class': 'form-control'}),
#             'timetable': forms.TextInput(attrs={'class': 'form-control'}),
#         }
#
# class ClassForm(forms.ModelForm):
#     class Meta:
#         model = CLASS
#         fields = ['class_name', 'course', 'begin_time', 'end_time']
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['course'].disabled = True
# class LessonForm(forms.ModelForm):
#     class Meta:
#         model = LESSON
#         fields = ['lesson_name', 'session_number', 'description']
#         widgets = {
#             'lesson_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'session_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }
# class LessonDetailForm(forms.ModelForm):
#     class Meta:
#         model = LESSON_DETAIL
#         fields = ['date']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#         }
#
# forms.py
from django import forms
from django.forms import modelformset_factory
from english.models import CLASS, LESSON_DETAIL, LESSON

class ClassUpdateForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time', 'status', 'timetable']
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'begin_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'timetable': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        begin_time = cleaned_data.get('begin_time')
        end_time = cleaned_data.get('end_time')
        if begin_time and end_time and end_time < begin_time:
            raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")
        return cleaned_data

class ClassForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time']
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'begin_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        begin_time = cleaned_data.get('begin_time')
        end_time = cleaned_data.get('end_time')
        if begin_time and end_time and end_time < begin_time:
            raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")
        return cleaned_data

class LessonForm(forms.ModelForm):
    class Meta:
        model = LESSON
        fields = ['lesson_name', 'session_number', 'description']
        widgets = {
            'lesson_name': forms.TextInput(attrs={'class': 'form-control'}),
            'session_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        # Kiểm tra xem instance đã có classes hay chưa
        if hasattr(self.instance, 'classes') and self.instance.classes:
            class_instance = self.instance.classes
            if date and (date < class_instance.begin_time or date > class_instance.end_time):
                raise forms.ValidationError("Ngày học phải nằm trong khoảng từ ngày bắt đầu đến ngày kết thúc của lớp.")
        return date

# Định nghĩa LessonDetailFormSet
LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    extra=0,  # Không cho phép thêm mới form trong formset
    can_delete=False  # Không cho phép xóa form trong formset
)