from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from english.models import USER_PROFILE


class ProfileForm(forms.ModelForm):
    class Meta:
        model = USER_PROFILE
        fields = ['dob', 'sex', 'description', 'image']
        widgets = {
            'dob': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'dd/mm/yyyy'
                },
                format='%Y-%m-%d'
            ),
            'sex': forms.Select(
                attrs={
                    'class': 'form-control select2',
                    'style': 'width: 100%'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': _('Nhập mô tả về bản thân...')
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class': 'form-control-file',
                    'accept': 'image/*',
                    'id': 'avatarUpload'
                }
            )
        }
        labels = {
            'dob': _('Ngày sinh'),
            'sex': _('Giới tính'),
            'description': _('Mô tả bản thân'),
            'image': _('Ảnh đại diện')
        }
        help_texts = {
            'image': _('Chỉ chấp nhận file ảnh (JPEG, PNG)')
        }

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError(_('Kích thước ảnh quá lớn (tối đa 2MB)'))
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise ValidationError(_('Chỉ chấp nhận file ảnh JPG/PNG'))
        return image


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Cập nhật attributes cho tất cả các trường
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu hiện tại'),
            'autocomplete': 'current-password'
        })

        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Nhập mật khẩu mới'),
            'autocomplete': 'new-password'
        })

        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Nhập lại mật khẩu mới'),
            'autocomplete': 'new-password'
        })

        # Cải thiện help text
        self.fields['new_password1'].help_text = _(
            "Mật khẩu phải chứa ít nhất 8 ký tự, bao gồm chữ số và ký tự đặc biệt."
        )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', _('Mật khẩu không khớp'))

        return cleaned_data


class EmailChangeForm(forms.Form):
    email = forms.EmailField(
        label=_("Email mới"),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@gmail.com'
        })
    )

    verification_code = forms.CharField(
        label=_("Mã xác nhận"),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mã 6 chữ số',
            'disabled': True
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user and self.user.email:
            self.fields['current_email'] = forms.CharField(
                label=_("Email hiện tại"),
                initial=self.user.email,
                widget=forms.TextInput(attrs={
                    'class': 'form-control',
                    'disabled': True
                })
            )
            self.fields['email'].label = _("Email mới")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email == getattr(self.user, 'email', None):
            raise ValidationError(_("Email mới phải khác email hiện tại"))
        return email
# from django import forms
# from django.contrib.auth.forms import PasswordChangeForm
# from english.models import USER_PROFILE
#
# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = USER_PROFILE
#         fields = ['dob', 'sex', 'description', 'image']
#         widgets = {
#             'dob': forms.DateInput(attrs={'type': 'date'}),
#             'sex': forms.Select(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3}),
#         }
#
# class CustomPasswordChangeForm(PasswordChangeForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields:
#             self.fields[field].widget.attrs.update({'class': 'form-control'})
#
# class EmailChangeForm(forms.Form):
#     email = forms.EmailField(label="Email mới")
#     verification_code = forms.CharField(label="Mã xác nhận", required=False)

# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from .models import USER_PROFILE
# from django.contrib.auth.forms import PasswordChangeForm
#
# class CustomPasswordChangeForm(PasswordChangeForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Thêm class Bootstrap cho các trường
#         self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
#         self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
#         self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
#
#
# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField(required=True)
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
#             'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
#         }
#
#
# class UserUpdateForm(forms.ModelForm):
#     email = forms.EmailField(required=True, label="Email")
#     first_name = forms.CharField(required=True, max_length=30, label="Tên")
#     last_name = forms.CharField(required=True, max_length=150, label="Họ")
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'first_name', 'last_name']
#         widgets = {
#             'username': forms.TextInput(attrs={'class': 'form-control'}),
#             'email': forms.EmailInput(attrs={'class': 'form-control'}),
#             'first_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'last_name': forms.TextInput(attrs={'class': 'form-control'}),
#         }
#         labels = {
#             'username': 'Tên đăng nhập',
#         }
#
#
# class ProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = USER_PROFILE
#         fields = ['dob', 'sex', 'description', 'image']
#         widgets = {
#             'dob': forms.DateInput(attrs={
#                 'class': 'form-control',
#                 'type': 'date'  # This will show a date picker in modern browsers
#             }),
#             'sex': forms.Select(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3
#             }),
#             'image': forms.FileInput(attrs={'class': 'form-control'}),
#         }
#         labels = {
#             'dob': 'Date of Birth',
#             'sex': 'Gender',
#             'description': 'About Me',
#             'image': 'Profile Picture',
#         }
# # from django import forms
# # from django.contrib.auth.models import User
# # from english.models import USER_PROFILE
# #
# #
# # class ProfileForm(forms.ModelForm):
# #     # Thêm các trường từ User model
# #     first_name = forms.CharField(label='Họ và tên đệm', required=False)
# #     last_name = forms.CharField(label='Tên', required=False)
# #
# #     class Meta:
# #         model = USER_PROFILE
# #         fields = ['dob', 'sex', 'description', 'image']
# #         labels = {
# #             'dob': 'Ngày sinh',
# #             'sex': 'Giới tính',
# #             'description': 'Mô tả của bạn',
# #             'image': 'Ảnh đại diện'
# #         }
# #         widgets = {
# #             'dob': forms.DateInput(attrs={'type': 'date'}),
# #             'description': forms.Textarea(attrs={'rows': 3}),
# #         }
# #
# #     def __init__(self, *args, **kwargs):
# #         super().__init__(*args, **kwargs)
# #         # Điền giá trị ban đầu từ User model nếu có
# #         if self.instance and self.instance.userprofile:
# #             user = self.instance.userprofile
# #             self.fields['first_name'].initial = user.first_name
# #             self.fields['last_name'].initial = user.last_name
# #
# #     def save(self, commit=True):
# #         profile = super().save(commit=False)
# #         if commit:
# #             # Lưu thông tin profile
# #             profile.save()
# #             # Cập nhật thông tin User
# #             if profile.userprofile:
# #                 user = profile.userprofile
# #                 user.first_name = self.cleaned_data['first_name']
# #                 user.last_name = self.cleaned_data['last_name']
# #                 user.save()
# #         return profile