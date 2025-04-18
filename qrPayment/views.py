import base64

from django.shortcuts import render

from english.models import PAYMENT


# Create your views here.
def qr_payment(request):
    return render(request, 'qr_payment.html')

def payment_list(request):
    # payments = PAYMENT.objects.select_related('course')
    #
    # # Chuyển QR binary sang base64 để hiển thị ảnh
    # for p in payments:
    #     if p.qr:
    #         p.qr_base64 = base64.b64encode(p.qr).decode('utf-8')
    #     else:
    #         p.qr_base64 = None
    #
    # return render(request, 'payment_list.html', {'payments': payments})
    return render(request, 'payment_list.html')
