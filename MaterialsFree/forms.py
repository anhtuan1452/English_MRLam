from django import forms

class DocumentSearchForm(forms.Form):
    search = forms.CharField(
        label='Tìm kiếm tài liệu',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên tài liệu...'})
    )
