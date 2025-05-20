from django.shortcuts import render, redirect
from english.models import COURSE, PAYMENT, PAYMENT_INFO, USER_CLASS, CLASS
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import time

@login_required
def start_payment(request, course_id):
    # Lấy thông tin khóa học
    course = COURSE.objects.get(course_id=course_id)

    # Lấy danh sách các lớp thuộc khóa học
    classes = CLASS.objects.filter(course=course)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        class_id = request.POST.get('class_id')

        # Kiểm tra nếu user đã đăng ký đúng lớp này rồi thì không cho phép
        already_registered = USER_CLASS.objects.filter(
            user=request.user,
            classes__class_id=class_id
        ).exists()

        if already_registered:
            return render(request, 'payment_form.html', {
                'course': course,
                'classes': classes,
                'error_message': 'Bạn đã đăng ký lớp này rồi.'
            })

        # Lấy thông tin thanh toán của khóa học
        payment = PAYMENT.objects.filter(course_id=course).first()

        # Tạo thông tin thanh toán
        payment_info = PAYMENT_INFO.objects.create(
            payment=payment,
            user=request.user,
            message=f"Đăng ký {course.course_name} - {phone}",
            time_at=timezone.now()
        )

        # Lưu class_id vào session để sau khi thanh toán xong gán vào USER_CLASS
        request.session['class_id'] = class_id
        print("Redirecting to QR:", payment_info.paymentinfo_id)

        return redirect(f'/payment/qr/{payment_info.paymentinfo_id}/')

    return render(request, 'payment_form.html', {
        'course': course,
        'classes': classes,
    })


@login_required
def qr_code_view(request, paymentinfo_id):
    # Lấy thông tin thanh toán từ database
    payment_info = PAYMENT_INFO.objects.get(paymentinfo_id=paymentinfo_id)
    return render(request, 'payment_qr.html', {
        'payment_info': payment_info
    })


@login_required
def payment_success(request, paymentinfo_id):
    # Lấy thông tin thanh toán từ database
    payment_info = PAYMENT_INFO.objects.get(paymentinfo_id=paymentinfo_id)
    user = request.user

    # Tạo USER_CLASS (đăng ký lớp học)
    class_id = request.session.get('class_id')
    if class_id:
        class_obj = CLASS.objects.get(class_id=class_id)
        USER_CLASS.objects.get_or_create(user=user, classes=class_obj)

    # Render trang thành công
    return render(request, 'payment_success.html', {'course': payment_info.payment.course_id})
