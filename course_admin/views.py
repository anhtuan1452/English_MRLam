from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages

from course_admin.forms import CourseForm, LessonDetailForm
from english.models import COURSE, LESSON_DETAIL, CLASS, LESSON, USER_PROFILE
from django.contrib.auth.models import User

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


User = get_user_model()

def admin_xemkhoahoc(request, course_id):
    course = get_object_or_404(COURSE, pk=course_id)
    classes = CLASS.objects.filter(course=course)
    lesson_details = LESSON_DETAIL.objects.filter(
        classes__in=classes,
        lesson__course=course
    ).select_related('lesson', 'classes') \
        .order_by('session_number')
    teachers = User.objects.filter(is_staff=True, is_superuser=False)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            # Xóa khóa học
            course.delete()
            messages.success(request, "Khóa học đã được xóa thành công!")
            return redirect('admin_ql_khoahoc')

        elif action == 'save':
            # Cập nhật khóa học
            course.course_name = request.POST.get('course_name', '').strip()
            course.description = request.POST.get('course_description', '').strip()
            teacher_id = request.POST.get('instructor')
            if teacher_id:
                teacher = User.objects.filter(pk=teacher_id, is_staff=True).first()
                if teacher:
                    course.teacher_name = teacher.get_full_name()

            # Xử lý giá
            price_text = request.POST.get('price', '').strip()
            if price_text.isdigit():
                course.price = int(price_text)
            else:
                messages.error(request, "Giá phải là số và không để trống")
                return render(request, 'course_admin_detail.html', {
                    'course': course,
                    'lesson_details': lesson_details,
                    'teachers': teachers,
                })

            course.save()
            messages.success(request, "Cập nhật khóa học thành công!")  # Thông báo lưu thành công
            return redirect('admin_ql_khoahoc')

    return render(request, 'course_admin_detail.html', {
        'course': course,
        'lesson_details': lesson_details,
        'teachers': teachers,
    })

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
def add_lesson_detail(request, course_id=None):
    if course_id:
        course = get_object_or_404(COURSE, pk=course_id)
    else:
        if request.method == 'POST':
            form = CourseForm(request.POST)
            if form.is_valid():
                course = form.save()
                # Tạo lớp mặc định cho khóa học mới
                default_class = CLASS.objects.create(course=course, class_name="Lớp mặc định")
                messages.success(request, 'Khóa học và lớp mới đã được tạo!')
                return redirect('admin_xemkhoahoc', course_id=course.pk)
            else:
                print(form.errors)
        else:
            form = CourseForm()

        return render(request, 'course_admin_add.html', {'form': form})

    # Nếu khóa học đã có, lấy lớp mặc định
    default_class = CLASS.objects.filter(course=course).first()
    if not default_class:
        messages.error(request, 'Chưa có lớp nào cho khóa học này.')
        return redirect('admin_xemkhoahoc', course_id=course.pk)

    if request.method == 'POST':
        form = LessonDetailForm(request.POST)
        if form.is_valid():
            # Tạo LESSON
            lesson = LESSON.objects.create(
                lesson_name=form.cleaned_data['lesson_name'],
                description=form.cleaned_data['description'],
                course=course
            )
            # Tạo LESSON_DETAIL với lớp mặc định
            LESSON_DETAIL.objects.create(
                lesson=lesson,
                classes=default_class,
                session_number=form.cleaned_data['session_number']
            )
            messages.success(request, "Thêm buổi học thành công!")
            return redirect('admin_xemkhoahoc', course_id=course.pk)
        else:
            # Nếu form không hợp lệ, in ra lỗi
            print(form.errors)
    else:
        form = LessonDetailForm()

    return render(request, 'lesson_admin_detail.html', {
        'course': course,
        'form': form,
    })



def view_lesson_detail(request, course_id=None, lesson_detail_id=None):
    course = get_object_or_404(COURSE, pk=course_id)

    # Lấy bài học nếu có lesson_detail_id
    if lesson_detail_id:
        lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
        lesson = lesson_detail.lesson
    else:
        lesson_detail = None  # Nếu không có lesson_detail_id, tạo mới bài học
        lesson = None

    if request.method == 'POST':
        if 'delete' in request.POST:  # Kiểm tra xem có yêu cầu xóa hay không
            lesson_detail.delete()
            return redirect('admin_xemkhoahoc', course_id=course.pk)  # Chuyển hướng sau khi xóa

        form = LessonDetailForm(request.POST, instance=lesson_detail)  # Truyền dữ liệu vào form
        if form.is_valid():
            # Cập nhật hoặc tạo mới bài học
            if lesson:
                # Cập nhật bài học hiện tại
                lesson.lesson_name = form.cleaned_data['lesson_name']
                lesson.description = form.cleaned_data['description']
                lesson.save()
            else:
                # Tạo mới bài học nếu chưa có
                lesson = LESSON.objects.create(
                    lesson_name=form.cleaned_data['lesson_name'],
                    description=form.cleaned_data['description'],
                    course=course
                )

            # Cập nhật hoặc tạo mới LESSON_DETAIL
            if lesson_detail:
                lesson_detail.lesson = lesson  # Cập nhật lesson
                lesson_detail.session_number = form.cleaned_data['session_number']
                lesson_detail.save()  # Lưu cập nhật
            else:
                # Tạo mới LESSON_DETAIL nếu chưa có
                default_class = CLASS.objects.filter(course=course).first()
                if not default_class:
                    messages.error(request, "Không có lớp mặc định cho khóa học này!")
                    return redirect('admin_xemkhoahoc', course_id=course.pk)
                LESSON_DETAIL.objects.create(
                    lesson=lesson,
                    classes=default_class,
                    session_number=form.cleaned_data['session_number']
                )

            messages.success(request, "Cập nhật buổi học thành công!")
            return redirect('admin_xemkhoahoc', course_id=course.pk)  # Chuyển hướng sau khi cập nhật
        else:
            messages.error(request, "Có lỗi xảy ra khi cập nhật buổi học.")
            print(form.errors)  # In ra lỗi form nếu có
    else:
        form = LessonDetailForm(instance=lesson_detail)

    return render(request, 'lesson_admin_detail.html', {
        'course': course,
        'form': form,
        'lesson_detail': lesson_detail,
    })