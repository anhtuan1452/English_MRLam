
from django import forms
from english.models import CLASS, LESSON_DETAIL, COURSE


class ClassUpdateForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time', 'timetable']
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'begin_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'timetable': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        begin_time = cleaned_data.get('begin_time')
        end_time = cleaned_data.get('end_time')
        if begin_time and end_time and end_time <= begin_time:
            raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")
        return cleaned_data


class ClassForm(forms.ModelForm):
    class Meta:
        model = CLASS
        fields = ['class_name', 'course', 'begin_time', 'end_time', 'timetable']  # Đã loại 'status'
        widgets = {
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'begin_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_time': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'timetable': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = COURSE.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        begin_time = cleaned_data.get('begin_time')
        end_time = cleaned_data.get('end_time')
        if begin_time and end_time and end_time <= begin_time:
            raise forms.ValidationError("Ngày kết thúc phải sau ngày bắt đầu.")
        return cleaned_data



class LessonDetailForm(forms.ModelForm):
    class Meta:
        model = LESSON_DETAIL
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date is None:
            return date

        # Kiểm tra xem instance có liên kết với classes không
        if hasattr(self.instance, 'classes') and self.instance.classes:
            class_instance = self.instance.classes
            if date < class_instance.begin_time or date > class_instance.end_time:
                raise forms.ValidationError("Ngày học phải nằm trong khoảng từ ngày bắt đầu đến ngày kết thúc của lớp.")
        return date
