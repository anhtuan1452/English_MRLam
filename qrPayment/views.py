from django.shortcuts import render

# Create your views here.
def qr_payment(request):
    return render(request, 'qr_payment.html')