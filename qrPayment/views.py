import base64

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from english.models import PAYMENT, PAYMENT_INFO
from qrPayment.forms import PaymentForm


def payment_list(request):
    # Lấy tất cả các đối tượng PAYMENT từ cơ sở dữ liệu
    payments = PAYMENT.objects.all()

    # Truyền payments vào context để hiển thị trong template
    return render(request, 'payment_list.html', {'payments': payments})

def payment_detail(request, payment_id):
    payment = get_object_or_404(PAYMENT, pk=payment_id)  # Lấy thông tin thanh toán theo ID
    payment_infos = PAYMENT_INFO.objects.filter(payment_id=payment_id).order_by(
        '-time_at')  # Lấy các thông tin thanh toán liên quan

    paginator = Paginator(payment_infos, 7)  # 7 dòng/trang
    page_number = request.GET.get('page', 1)  # ?page=1 nếu không có param
    page_obj = paginator.get_page(page_number)
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES, instance=payment)  # Truyền instance để chỉnh sửa
        if 'delete' in request.POST:  # Kiểm tra xem nút "Xóa" có được nhấn không
            payment.delete()  # Xóa thanh toán
            return redirect('payment_list')  # Sau khi xóa, chuyển hướng về danh sách thanh toán
        elif form.is_valid():
            form.save()  # Lưu thông tin thanh toán đã chỉnh sửa
            return redirect('payment_list')  # Sau khi lưu, chuyển hướng về danh sách thanh toán
    else:
        form = PaymentForm(instance=payment)  # Nếu là GET, hiển thị form với dữ liệu của thanh toán cần chỉnh sửa

    return render(request, 'payment_detail.html',
                  {'form': form, 'payment_detail': payment, 'payment_infos': payment_infos, 'page_obj': page_obj})  # Trả về form chỉnh sửa thanh toán
def add_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST, request.FILES)  # Xử lý file upload
        if form.is_valid():
            form.save()  # Lưu thông tin thanh toán mới vào cơ sở dữ liệu
            return redirect('payment_list')  # Sau khi lưu, chuyển hướng về danh sách thanh toán
    else:
        form = PaymentForm()  # Nếu là GET, hiển thị form mới

    return render(request, 'add_payment.html', {'form': form})