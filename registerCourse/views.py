from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from english.models import COURSE, PAYMENT

def payment_view(request):
    course = get_object_or_404(COURSE, course_id=1)
    payment = PAYMENT.objects.filter(course=course).first()  # Assuming each course has one payment method

    # When the form is submitted, you can handle the POST data here
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        schedule = request.POST.get('schedule')

        # Handle form data (e.g., save to database or process payment)

    context = {
        'course': course,
        'payment': payment
    }

    return render(request, 'payment_page.html', context)

