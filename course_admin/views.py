import base64

from django.shortcuts import render, get_object_or_404

from english.models import COURSE, LESSON_DETAIL, CLASS, ACCOUNT, LESSON


# Create your views here.
def admin_ql_khoahoc(request):
    courses = COURSE.objects.all()
    return render(request, 'course_admin_home.html', {'courses': courses})
def admin_xemkhoahoc(request, course_id):
    course = get_object_or_404(COURSE, pk=course_id)
    classes = CLASS.objects.filter(course=course)
    lesson_details = LESSON_DETAIL.objects.filter(
        class_instance__in=classes,
        lesson__course=course
    ).select_related('lesson', 'class_instance')

    # Lấy danh sách giáo viên từ Account
    teachers = ACCOUNT.objects.filter(role='teacher')

    return render(request, 'course_admin_detail.html', {
        'course': course,
        'lesson_details': lesson_details,
        'teachers': teachers,
    })
def add_lesson_detail(request, course_id):
    course = get_object_or_404(COURSE, pk=course_id)
    classes = CLASS.objects.filter(course=course)
    lessons = LESSON.objects.filter(course=course)
    teachers = ACCOUNT.objects.filter(account__role='teacher')

    return render(request, 'lesson_admin_detail.html', {
        'course': course,
        'classes': classes,
        'lessons': lessons,
        'teachers': teachers,
    })