from django import forms
from .models import TaiLieu, KhoaHoc

class TaiLieuForm(forms.ModelForm):
    class Meta:
        model = TaiLieu
        fields = ['ma_tai_lieu', 'ten_tai_lieu', 'mo_ta', 'khoa_hoc', 'file_tai_lieu']
        widgets = {
            'ma_tai_lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'ten_tai_lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'mo_ta': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'khoa_hoc': forms.Select(attrs={'class': 'form-control'}),
            'file_tai_lieu': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'ma_tai_lieu': 'Mã tài liệu',
            'ten_tai_lieu': 'Tên tài liệu',
            'mo_ta': 'Mô tả',
            'khoa_hoc': 'Khóa học',
            'file_tai_lieu': 'File tài liệu',
        }

