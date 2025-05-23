from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages

from course_admin.forms import CourseForm, LessonForm
from english.models import COURSE, LESSON_DETAIL, CLASS, LESSON, USER_PROFILE
from django.contrib.auth.models import User

from english.views import superuser_required


@superuser_required
def admin_ql_khoahoc(request):
    # 1) Lấy q từ querystring (URL ?q=...)
    q = request.GET.get('q', '').strip()

    # 2) Khởi tạo queryset cơ bản
    courses = COURSE.objects.all()

    # 3) Nếu có q thì filter
    if q:
        courses = courses.filter(
            Q(course_name__icontains=q) |
            Q(description__icontains=q) |
            Q(teacher_name__icontains=q) |
            Q(des_teacher__icontains=q)
        )

    # 4) Trả về template, kèm luôn q để giữ lại value trong input
    return render(request, 'course_admin_home.html', {
        'courses': courses,
        'q': q,
    })


@superuser_required
def admin_xemkhoahoc(request, course_id):
    course = get_object_or_404(COURSE, pk=course_id)
    classes = CLASS.objects.filter(course=course)
    lessons = LESSON.objects.filter(course=course).order_by('session_number')
    teachers = User.objects.filter(is_staff=True, is_superuser=False)


    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            course.delete()
            messages.success(request, "Khóa học đã được xóa thành công!")
            return redirect('admin_ql_khoahoc')

        elif action == 'save':
            course.course_name = request.POST.get('course_name', '').strip()
            course.description = request.POST.get('course_description', '').strip()
            image_file = request.FILES.get('image')
            if image_file:
                course.image = image_file

            remove_image = request.POST.get('remove_image')
            if remove_image and course.image:
                course.image.delete(save=False)  # Xóa file vật lý
                course.image = None
            teacher_id = request.POST.get('instructor')
            if teacher_id:
                teacher = User.objects.filter(pk=teacher_id, is_staff=True).first()
                if teacher:
                    course.teacher_name = teacher.get_full_name()

            price_text = request.POST.get('price', '').strip()
            try:
                course.price = int(price_text)
            except ValueError:
                messages.error(request, "Giá phải là số nguyên và không để trống")
                return render(request, 'course_admin_detail.html', {
                    'course': course,
                    'lessons': lessons,
                    'teachers': teachers,
                })

            course.save()
            messages.success(request, "Cập nhật khóa học thành công!")
            return redirect('admin_ql_khoahoc')

    return render(request, 'course_admin_detail.html', {
        'course': course,
        'lessons': lessons,
        'teachers': teachers,
    })



@superuser_required
def admin_themkhoahoc(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Thêm khóa học thành công!")  # Thông báo lưu thành công
            return redirect('admin_ql_khoahoc')
    else:
        form = CourseForm()
    return render(request, 'course_admin_add.html', {
        'form': form,
    })
@superuser_required
def add_lesson(request, course_id=None):
    if not course_id:
        messages.error(request, "Không có khóa học để thêm buổi học.")
        return redirect('admin_ql_khoahoc')

    course = get_object_or_404(COURSE, pk=course_id)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Thêm buổi học thành công!")
            return redirect('admin_xemkhoahoc', course_id=course.pk)
        else:
            messages.error(request, form.errors.as_text())
    else:
        form = LessonForm()

    return render(request, 'lesson_admin_detail.html', {
        'course': course,
        'form': form,
    })

@superuser_required
def view_lesson(request, course_id=None, lesson_id=None):
    course = get_object_or_404(COURSE, pk=course_id)
    lesson = get_object_or_404(LESSON, pk=lesson_id) if lesson_id else None

    if request.method == 'POST':
        if 'delete' in request.POST and lesson:
            lesson.delete()
            messages.success(request, "Xóa bài học thành công!")
            return redirect('admin_xemkhoahoc', course_id=course.pk)

        form = LessonForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, "Cập nhật bài học thành công!")
            return redirect('admin_xemkhoahoc', course_id=course.pk)
        else:
            messages.error(request, form.errors.as_text())
            print(form.errors)
    else:
        form = LessonForm(instance=lesson)

    return render(request, 'lesson_admin_detail.html', {
        'course': course,
        'form': form,
        'lesson': lesson,
    })