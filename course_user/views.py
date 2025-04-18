from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from english.models import COURSE, CLASS


def course(request):
    courses = COURSE.objects.all()
    classes = CLASS.objects.all()
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

