import datetime
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from english.models import LESSON, LESSON_DETAIL, EXERCISE, CLASS, SUBMISSION
from exercise_admin.forms import ExerciseForm

from english.views import is_admin, is_staff


# Quản lý bài tập + tìm kiếm
@login_required
@user_passes_test(is_staff)
def admin_ql_baitap(request):
    q = request.GET.get('q', '').strip()

    # Lấy danh sách bài tập, join đến LESSON_DETAIL, LESSON, CLASS để lấy thông tin
    exercises = EXERCISE.objects.select_related('lessondetail__lesson', 'lessondetail__classes').all()

    if q:
        filters = (
            Q(lessondetail__classes__class_name__icontains=q) |
            Q(lessondetail__lesson__lesson_name__icontains=q) |
            Q(lessondetail__lesson__description__icontains=q)
        )
        if q.isdigit():
            filters |= Q(lessondetail__lesson__lesson_id=q)
        exercises = exercises.filter(filters)

    context = {
        'exercises': exercises,
        'query': q,
    }
    return render(request, 'ql_baitap.html', context)
@login_required
@user_passes_test(is_staff)
def them_baitap(request):
    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES)
        if form.is_valid():
            class_selected = form.cleaned_data['class_selected']
            session_number = form.cleaned_data['session_number']
            description = form.cleaned_data['description']
            lesson_file = form.cleaned_data['lesson_file']
            exercise_file = form.cleaned_data['exercise_file']
            date = form.cleaned_data['date']

            # Kiểm tra xem class có tồn tại
            class_instance = get_object_or_404(CLASS, pk=class_selected.pk)

            # Kiểm tra xem lớp đã có LESSON_DETAIL với session_number này chưa
            existing_lesson_detail = LESSON_DETAIL.objects.filter(
                classes=class_instance,
                lesson__session_number=session_number
            ).select_related('lesson').first()

            if existing_lesson_detail:
                messages.error(request, f"Buổi {session_number} đã tồn tại cho lớp {class_instance.class_name}. Vui lòng chọn số buổi khác hoặc chỉnh sửa.")
                return render(request, 'thembt.html', {'form': form})

            # Tạo LESSON mới với class_specific_id
            lesson = LESSON.objects.create(
                lesson_name=f"Buổi {session_number} - {class_instance.class_name}",
                description=description,
                session_number=session_number,
                course=class_instance.course,
                lesson_file=lesson_file,
                exercise_file=exercise_file,
                class_specific_id=class_instance.class_id  # Gán class_id để đánh dấu LESSON thuộc về lớp này
            )

            # Tạo LESSON_DETAIL chỉ cho lớp này
            lesson_detail = LESSON_DETAIL.objects.create(
                lesson=lesson,
                classes=class_instance,
                date=date
            )

            # Tạo EXERCISE
            EXERCISE.objects.create(
                lessondetail=lesson_detail,
                duedate=date
            )

            messages.success(request, "Thêm bài tập thành công!")
            return redirect('admin_ql_baitap')
        else:
            messages.error(request, "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.")
    else:
        form = ExerciseForm()

    return render(request, 'thembt.html', {
        'form': form,
    })
@login_required
@user_passes_test(is_staff)
def xem_baitap(request, lesson_detail_id):
    lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
    try:
        exercise = lesson_detail.exercise
    except EXERCISE.DoesNotExist:
        exercise = None

    class_list = CLASS.objects.all()

    if request.method == 'POST':
        class_selected_id = request.POST.get('class_selected')
        session_number = request.POST.get('session_number')
        lesson_name = request.POST.get('lesson_name')
        description = request.POST.get('description')
        date_str = request.POST.get('date')

        # Cập nhật lớp học
        if class_selected_id:
            try:
                selected_class = CLASS.objects.get(pk=class_selected_id)
                lesson_detail.classes = selected_class
                lesson_detail.save()
            except CLASS.DoesNotExist:
                messages.error(request, "Lớp học không tồn tại.")
                return redirect('admin_ql_baitap')

        # Cập nhật lesson
        lesson = lesson_detail.lesson
        if session_number:
            try:
                lesson.session_number = int(session_number)
            except ValueError:
                messages.error(request, "Số buổi học không hợp lệ.")
        if lesson_name:
            lesson.lesson_name = lesson_name
        if description:
            lesson.description = description
        lesson.save()

        # Cập nhật ngày buổi học
        if date_str:
            try:
                new_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                lesson_detail.date = new_date
                lesson_detail.save()
            except ValueError:
                messages.error(request, "Ngày không hợp lệ.")

        # Cập nhật hoặc tạo mới exercise
        if not exercise:
            exercise = EXERCISE.objects.create(
                lessondetail=lesson_detail,
                duedate=new_date
            )
        else:
            exercise.duedate = new_date
            exercise.save()

        # Xử lý file upload
        if 'lesson_file' in request.FILES:
            lesson.lesson_file = request.FILES['lesson_file']
            lesson.save()
        if 'exercise_file' in request.FILES:
            lesson.exercise_file = request.FILES['exercise_file']
            lesson.save()

        messages.success(request, "Cập nhật bài tập thành công!")
        return redirect('admin_ql_baitap')

    return render(request, 'xembt.html', {
        'lesson_detail': lesson_detail,
        'exercise': exercise,
        'class_list': class_list,
    })
@login_required
@user_passes_test(is_staff)
def sua_baitap(request, lesson_detail_id):
    lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
    lesson = lesson_detail.lesson
    exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()

    if request.method == 'POST':
        form = ExerciseForm(request.POST, request.FILES, lesson_detail_id=lesson_detail_id)
        if form.is_valid():
            class_selected = form.cleaned_data['class_selected']
            session_number = form.cleaned_data['session_number']
            lesson_name = form.cleaned_data['lesson_name']
            description = form.cleaned_data['description']
            lesson_file = form.cleaned_data.get('lesson_file')
            exercise_file = form.cleaned_data.get('exercise_file')
            date = form.cleaned_data['date']

            # Cập nhật lesson
            lesson.lesson_name = lesson_name
            lesson.description = description
            lesson.session_number = session_number
            lesson.course = class_selected.course
            if lesson_file:
                lesson.lesson_file = lesson_file
            if exercise_file:
                lesson.exercise_file = exercise_file
            lesson.save()

            # Cập nhật lesson_detail
            lesson_detail.classes = class_selected
            lesson_detail.date = date
            lesson_detail.save()

            # Cập nhật hoặc tạo mới exercise
            if exercise:
                exercise.duedate = date
                exercise.save()
            else:
                exercise = EXERCISE.objects.create(
                    lessondetail=lesson_detail,
                    duedate=date
                )

            messages.success(request, "Cập nhật bài tập thành công!")
            return redirect('admin_ql_baitap')
        else:
            messages.error(request, "Dữ liệu không hợp lệ. Vui lòng kiểm tra lại.")
    else:
        form = ExerciseForm(initial={
            'class_selected': lesson_detail.classes,
            'session_number': lesson.session_number,
            'lesson_name': lesson.lesson_name,
            'description': lesson.description,
            'date': lesson_detail.date,
        }, lesson_detail_id=lesson_detail_id)

    return render(request, 'suabt.html', {
        'form': form,
        'lesson_detail': lesson_detail,
        'lesson': lesson,
        'exercise': exercise,
        'class_list': CLASS.objects.all(),
    })

@login_required
@user_passes_test(is_staff)
def xoa_baitap(request, lesson_detail_id):
    lesson_detail = get_object_or_404(LESSON_DETAIL, pk=lesson_detail_id)
    lesson = lesson_detail.lesson

    # Xóa các SUBMISSION liên quan
    exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
    if exercise:
        SUBMISSION.objects.filter(exercise=exercise).delete()
        exercise.delete()

    # Xóa LESSON_DETAIL
    lesson_detail.delete()

    # Xóa LESSON nếu không còn LESSON_DETAIL nào liên kết
    if not LESSON_DETAIL.objects.filter(lesson=lesson).exists():
        lesson.delete()

    messages.success(request, "Đã xóa bài tập thành công.")
    return redirect('admin_ql_baitap')
