from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from english.models import UserClass, UserProfile, Course, Class


def course(request):
    courses = Course.objects.all()
    classes = Class.objects.all()
    context = {
        'courses': courses,
        'classes': classes,
    }

    return render(request, 'courses.html', context)


def course_detail(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    # Lấy danh sách bài học (giả sử bạn có liên kết course.lessons)
    lessons = course.lessons.all() if hasattr(course, 'lessons') else []
    # Lấy danh sách khóa học khác (giả sử bạn có liên kết course.other_courses)
    other_courses = Course.objects.exclude(course_id=course_id)  # Lấy tất cả khóa học ngoại trừ khóa học hiện tại


    context = {
        'course': course,
        'lessons': lessons,
        'courses': other_courses,  # dùng trong phần "Khóa học khác"
    }
    return render(request, 'course_detail.html', context)

