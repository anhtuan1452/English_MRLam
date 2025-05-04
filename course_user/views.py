from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from english.models import COURSE, CLASS, USER_CLASS

def course(request):
    # Lấy tất cả khóa học
    courses = COURSE.objects.all()

    # Nếu người dùng đã đăng nhập, lấy lớp học của họ
    if request.user.is_authenticated:
        # Lấy các lớp học mà người dùng đã đăng ký
        user_classes = USER_CLASS.objects.filter(user=request.user).values_list('classes', flat=True)

        # Lọc các lớp học đã đăng ký của người dùng
        classes = CLASS.objects.filter(class_id__in=user_classes)
    else:
        classes = []

    context = {
        'courses': courses,
        'classes': classes,
    }

    return render(request, 'courses.html', context)

def course_detail(request, course_id):
    course = get_object_or_404(COURSE, course_id=course_id)

    lessons = course.lesson_set.all()
    other_courses = COURSE.objects.exclude(course_id=course_id)  # Lấy tất cả khóa học ngoại trừ khóa học hiện tại
    context = {
        'course': course,
        'lessons': lessons,
        'courses': other_courses,  # dùng trong phần "Khóa học khác"
    }
    return render(request, 'course_detail.html', context)

