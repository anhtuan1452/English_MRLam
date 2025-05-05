from django import forms

class DocumentSearchForm(forms.Form):
    search = forms.CharField(
        label='Tìm kiếm tài liệu',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên tài liệu...'})
    )
class DocumentUploadForm(forms.Form):
    doc_name = forms.CharField(max_length=255)
    doc_file = forms.FileField()
