import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.forms import modelformset_factory
from django.utils.timezone import now

from django.contrib.auth.models import User

from ManageClass.forms import  ClassUpdateForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE,
    ROLLCALL, ROLLCALL_USER, SUBMISSION, EXERCISE,
    LESSON, LESSON_DETAIL
)
from course_admin.forms import LessonDetailForm, LessonDetailFormSet

# Danh sách lớp học
def class_list(request):
    query = request.GET.get("q")
    classes = CLASS.objects.all()

    if query:
        classes = classes.filter(class_name__icontains=query)

    classes = classes.annotate(student_count=Count('user_class'))

    return render(request, 'class_list.html', {
        'classes': classes,
        'now': now().date(),
    })


def class_detail(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Fetching lessons related to the class via the course
    lesson_details = LESSON_DETAIL.objects.filter(lesson__course=class_instance.course).select_related('lesson')

    # Mặc định khởi tạo form
    class_form = ClassUpdateForm(instance=class_instance)
    lesson_form = LessonDetailForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_class':
            class_form = ClassUpdateForm(request.POST, instance=class_instance)
            if class_form.is_valid():
                class_form.save()
                return redirect('class_detail', class_id=class_instance.pk)

        elif action == 'add_lesson':
            lesson_form = LessonDetailForm(request.POST)
            if lesson_form.is_valid():
                lesson_detail = lesson_form.save(commit=False)

                # Tạo bài học mới và gán cho course của lớp học
                new_lesson = LESSON.objects.create(course=class_instance.course)
                lesson_detail.lesson = new_lesson
                lesson_detail.save()

                return redirect('class_detail', class_id=class_instance.pk)

    context = {
        'class_instance': class_instance,
        'lesson_details': lesson_details,
        'class_form': class_form,
        'form': lesson_form,
    }
    return render(request, 'class_detail.html', context)


# Bài tập trong lớp
def class_exercise(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    submissions = SUBMISSION.objects.filter(
        userclass__classes=class_instance
    ).select_related('userclass__user', 'exercise__lessondetail__lesson')

    if not submissions:
        submissions = None

    return render(request, 'class_exercise.html', {
        'class_instance': class_instance,
        'class_id': class_id,
        'submissions': submissions
    })

# Điểm danh trong lớp
def class_rollcall(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    lesson_details = LESSON_DETAIL.objects.filter(lesson__class_field=class_instance).select_related('lesson')

    rollcall_data = []
    for lesson_detail in lesson_details:
        rollcall_users = []
        rollcall = getattr(lesson_detail, 'rollcall', None)
        if rollcall:
            rollcall_users = ROLLCALL_USER.objects.filter(rollcall=rollcall).select_related('userclass__user')

        rollcall_data.append({
            'lesson_detail': lesson_detail,
            'rollcall_users': rollcall_users,
            'has_rollcall': rollcall is not None,
        })

    return render(request, 'class_rollcall.html', {
        'class_instance': class_instance,
        'rollcall_data': rollcall_data,
    })

# Thêm học viên vào lớp
def add_student_to_class(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, pk=user_id)
        USER_CLASS.objects.get_or_create(user=user, classes=class_instance)
        return redirect('class_detail', class_id=class_id)

    users_not_in_class = User.objects.exclude(
        id__in=USER_CLASS.objects.filter(classes=class_instance).values_list('user_id', flat=True)
    )
    return render(request, 'add_student_to_class.html', {
        'class_instance': class_instance,
        'users': users_not_in_class
    })

# Thêm lớp mới
def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})

# Cập nhật trạng thái điểm danh
def update_rollcall(request):
    if request.method == 'POST':
        rollcall_data = request.POST.get('rollcall_data')

        if rollcall_data:
            try:
                rollcall_data = json.loads(rollcall_data)

                for user_id, data in rollcall_data.items():
                    lesson_detail_id = data.get('lesson_detail_id')
                    status = data.get('status')

                    if not lesson_detail_id or not str(lesson_detail_id).isdigit():
                        continue

                    try:
                        lesson_detail = LESSON_DETAIL.objects.get(pk=lesson_detail_id)
                    except LESSON_DETAIL.DoesNotExist:
                        continue

                    try:
                        user = ROLLCALL_USER.objects.get(
                            userclass__user__id=user_id,
                            rollcall__lessondetail=lesson_detail
                        )
                        user.status = status
                        user.save()
                    except ROLLCALL_USER.DoesNotExist:
                        continue

                return JsonResponse({'message': 'Cập nhật trạng thái thành công!'})

            except Exception as e:
                return JsonResponse({'message': f'Lỗi xử lý dữ liệu: {str(e)}'}, status=400)

        return JsonResponse({'message': 'Dữ liệu gửi lên không hợp lệ'}, status=400)

    return JsonResponse({'message': 'Chỉ chấp nhận phương thức POST'}, status=405)

# Chi tiết bài tập trong lớp
def exercise_detail_view(request, class_id, exercise_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    exercise = get_object_or_404(EXERCISE, pk=exercise_id)

    submissions = SUBMISSION.objects.filter(
        exercise=exercise,
        userclass__classes=class_instance
    ).select_related('userclass__user')

    return render(request, 'exercise_detail.html', {
        'class_instance': class_instance,
        'exercise': exercise,
        'submissions': submissions,
    })

# Thêm danh sách buổi học vào khóa học
def add_lesson_details(request, course_id):
    course = get_object_or_404(COURSE, pk=course_id)
    default_class = CLASS.objects.filter(course=course).first()
    if not default_class:
        messages.error(request, "Chưa có lớp học cho khóa học này.")
        return redirect('admin_xemkhoahoc', course_id=course.pk)

    if request.method == 'POST':
        formset = LessonDetailFormSet(request.POST)
        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    if not form.cleaned_data:
                        continue

                    session_number = form.cleaned_data.get('session_number')
                    date = form.cleaned_data.get('date')

                    if session_number and date:
                        lesson = LESSON.objects.create(class_field=default_class)
                        LESSON_DETAIL.objects.create(
                            lesson=lesson,
                            session_number=session_number,
                            date=date
                        )
                messages.success(request, "Thêm buổi học thành công!")
                return redirect('admin_xemkhoahoc', course_id=course.pk)
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm buổi học.")
    else:
        formset = LessonDetailFormSet(queryset=LESSON_DETAIL.objects.none())

    return render(request, 'lesson_details.html', {
        'formset': formset,
        'course': course,
    })
