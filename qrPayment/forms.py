from django import forms
from django.forms import FileInput
from rest_framework.exceptions import ValidationError

from english.models import PAYMENT, COURSE


class PaymentForm(forms.ModelForm):
    qr = forms.ImageField(
        widget=FileInput  # <-- chỉ file input thuần
    )
    class Meta:
        model = PAYMENT
        fields = ['account_owner', 'account_number', 'bank_name', 'course_id', 'qr']
        labels = {
            'account_owner': 'Tên tài khoản',
            'account_number': 'Số tài khoản',
            'bank_name': 'Ngân hàng',
            'qr': 'QR code',
        }
    course_id = forms.ModelChoiceField(queryset=COURSE.objects.all(), empty_label="Chọn khóa học", label='Khóa học', required=True)