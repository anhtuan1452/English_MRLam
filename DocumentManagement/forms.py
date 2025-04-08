from django import forms
from english.models import Document  # Assuming models are in the same app


class DocumentForm(forms.ModelForm):
    # Add a description field that's not in the model but needed for the form
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Mô tả nội dung của tài liệu',
            'rows': 4
        }),
        label='Mô tả'
    )

    class Meta:
        model = Document
        fields = ['doc_name', 'doc_file']
        widgets = {
            'doc_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên tài liệu'
            }),
            'doc_file': forms.FileInput(attrs={
                'class': 'form-control-file',
                'style': 'display: none;'
            }),
        }
        labels = {
            'doc_name': 'Tên tài liệu',
            'doc_file': 'File tài liệu',
        }