import os

from django.conf import settings
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from english.models import COURSE, LESSON
from exercise_admin.forms import KhoaHocForm, BuoiHocForm

# Quản lý bài tập + tìm kiếm
def admin_ql_baitap(request):
    q = request.GET.get('q', '').strip()
    lessons = LESSON.objects.all()
    if q:
        filters = (
            Q(course__course_name__icontains=q) |
            Q(lesson_name__icontains=q) |
            Q(description__icontains=q)
        )
        if q.isdigit():
            filters |= Q(lesson_id=q)
        lessons = lessons.filter(filters)
    context = {
        'lessons': lessons,
        'query': q,
    }
    return render(request, 'ql_baitap.html', context)
# def admin_ql_baitap(request):
#     courses = COURSE.objects.all()  # Lấy tất cả các khóa học
#     lessons = LESSON.objects.select_related('course').all()  # Lấy tất cả các bài học với thông tin khóa học
#                                                             # SELECT * FROM lesson JOIN course ON lesson.course_id = course.id;(ví dụ)
#     context = {
#         'courses': courses,
#         'lessons': lessons,
#     }
#     return render(request, 'ql_baitap.html', context)

# Thêm bài tập
def them_baitap(request):
    if request.method == 'POST':
        form1 = KhoaHocForm(request.POST)
        form2 = BuoiHocForm(request.POST, request.FILES)

        if form1.is_valid() and form2.is_valid():
            # Lưu file upload từ form2
            if "file_upload" in request.FILES:
                save_path = os.path.join(settings.MEDIA_ROOT, request.FILES["file_upload"].name)
                with open(save_path, "wb") as output_file:
                    for chunk in request.FILES["file_upload"].chunks():
                        output_file.write(chunk)

            # Lưu thông tin khóa học và buổi học
            course = form1.save()
            lesson = form2.save(commit=False)
            lesson.course = course  # Gán khóa học cho buổi học
            lesson.save() # Thêm thông báo thành công
            messages.success(request, 'Thêm bài tập thành công!')
            return redirect('admin_ql_baitap')
    else:
        form1 = KhoaHocForm()
        form2 = BuoiHocForm()
    return render(request, 'thembt.html', {'form1': form1, 'form2': form2})

# Xem chi tiết bài tập
def xem_baitap(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)
    course = lesson.course

    if request.method == 'POST':
        form = BuoiHocForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()

            # Cập nhật tên khóa học nếu có trường course_name trong form
            course_name = request.POST.get('course_name')
            if course_name and course_name != course.course_name:
                course.course_name = course_name
                course.save()
            messages.success(request, 'Lưu thành công!')
            return redirect('xem_baitap', lesson_id=lesson.lesson_id)
    else:
        form = BuoiHocForm(instance=lesson)
    context = {
        'lesson': lesson,
        'course': course,
        'form': form,
    }
    return render(request, 'xembt.html', context)
# Sửa bài tập
def sua_baitap(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)
    # Lấy thông tin khóa học tương ứng với bài học
    course = lesson.course
    if request.method == 'POST':
        form = BuoiHocForm(request.POST, request.FILES, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('admin_ql_baitap')
    else:
        form = BuoiHocForm(instance=lesson)
    return render(request, 'suabt.html', {'form': form, 'lesson': lesson , 'course': course})
# Xóa bài tập
def xoa_baitap(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)

    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Đã xoá bài học thành công.')
        return redirect('admin_ql_baitap')

#sửa bt ở trang xem bài tập
def sua_baitap_xem(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)
    course = lesson.course
    if request.method == 'POST':
        form = BuoiHocForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            return redirect('admin_ql_baitap')
    else:
        form = BuoiHocForm(instance=lesson)
    return render(request, 'xembt.html', {'form': form, 'lesson': lesson , 'course': course})
