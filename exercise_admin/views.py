from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages

from english.models import COURSE, LESSON
from exercise_admin.forms import KhoaHocForm, BuoiHocForm

# Quản lý bài tập
def admin_ql_baitap(request):
    courses = COURSE.objects.all()  # Lấy tất cả các khóa học
    lessons = LESSON.objects.select_related('course').all()  # Lấy tất cả các bài học với thông tin khóa học
                                                            # SELECT * FROM lesson JOIN course ON lesson.course_id = course.id;(ví dụ)
    context = {
        'courses': courses,
        'lessons': lessons,
    }
    return render(request, 'ql_baitap.html', context)

# Thêm bài tập
def them_baitap(request):
    if request.method == 'POST':
        form1 = KhoaHocForm(request.POST)
        form2 = BuoiHocForm(request.POST)

        if form1.is_valid() and form2.is_valid():
            # Lưu thông tin khóa học và buổi học
            course = form1.save()
            lesson = form2.save(commit=False)
            lesson.course = course  # Gán khóa học cho buổi học
            lesson.save()
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
        form = BuoiHocForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            # Sau khi save xong, lấy lại dữ liệu mới nhất từ DB
            lesson.refresh_from_db()
            form = BuoiHocForm(instance=lesson)  # load lại form từ lesson mới
            return render(request, 'xembt.html', {
                'lesson': lesson,
                'course': course,
                'form': form,
                'success_message': 'Lưu thành công!',
            })
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
        form = BuoiHocForm(request.POST, instance=lesson)
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
        return render(request, 'ql_baitap.html', {'deleted': True})

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