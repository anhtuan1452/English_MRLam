from django import forms
from django.contrib.auth.models import User
from english.models import USER_PROFILE


class ProfileForm(forms.ModelForm):
    # Thêm các trường từ User model
    first_name = forms.CharField(label='Họ và tên đệm', required=False)
    last_name = forms.CharField(label='Tên', required=False)

    class Meta:
        model = USER_PROFILE
        fields = ['dob', 'sex', 'description', 'image']
        labels = {
            'dob': 'Ngày sinh',
            'sex': 'Giới tính',
            'description': 'Mô tả của bạn',
            'image': 'Ảnh đại diện'
        }
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Điền giá trị ban đầu từ User model nếu có
        if self.instance and self.instance.userprofile:
            user = self.instance.userprofile
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Lưu thông tin profile
            profile.save()
            # Cập nhật thông tin User
            if profile.userprofile:
                user = profile.userprofile
                user.first_name = self.cleaned_data['first_name']
                user.last_name = self.cleaned_data['last_name']
                user.save()
        return profile