from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from english.models import USER_PROFILE

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = USER_PROFILE
        fields = ['dob', 'sex', 'description', 'image']
        widgets = {
            'dob': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'Chọn ngày sinh'
                }
            ),
            'sex': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Giới thiệu ngắn gọn về bản thân...'
                }
            ),
            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }
        labels = {
            'dob': 'Ngày sinh',
            'sex': 'Giới tính',
            'description': 'Mô tả',
            'image': 'Ảnh đại diện'
        }


class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(PasswordChangeCustomForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu hiện tại'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu mới'
        })


class EmailUpdateForm(forms.Form):
    email = forms.EmailField(label="Email mới", required=True)
    verification_code = forms.CharField(label="Mã xác nhận", required=False)

