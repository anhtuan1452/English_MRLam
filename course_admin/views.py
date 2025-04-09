import base64

from django.shortcuts import render, get_object_or_404

from english.models import Course, LessonDetail, Class, Account, Lesson, UserProfile


# Create your views here.
def admin_ql_khoahoc(request):
    courses = Course.objects.all()
    return render(request, 'course_admin_home.html', {'courses': courses})
def admin_xemkhoahoc(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    classes = Class.objects.filter(course=course)
    lesson_details = LessonDetail.objects.filter(
        class_instance__in=classes,
        lesson__course=course
    ).select_related('lesson', 'class_instance')

    # Lấy danh sách giáo viên từ Account
    teachers = Account.objects.filter(role='teacher')

    return render(request, 'course_admin_detail.html', {
        'course': course,
        'lesson_details': lesson_details,
        'teachers': teachers,
    })
def add_lesson_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    classes = Class.objects.filter(course=course)
    lessons = Lesson.objects.filter(course=course)
    teachers = UserProfile.objects.filter(account__role='teacher')

    return render(request, 'lesson_admin_detail.html', {
        'course': course,
        'classes': classes,
        'lessons': lessons,
        'teachers': teachers,
    })