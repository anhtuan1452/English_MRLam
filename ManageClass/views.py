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

from ManageClass.forms import ClassUpdateForm, LessonForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER, SUBMISSION, EXERCISE,
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


# views.py
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

from ManageClass.forms import ClassUpdateForm, LessonForm
from english.models import (
    CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL_USER, SUBMISSION, EXERCISE,
    LESSON, LESSON_DETAIL
)
from course_admin.forms import LessonDetailForm, LessonDetailFormSet

# Create a formset for LessonDetailForm
LessonDetailFormSet = modelformset_factory(
    LESSON_DETAIL,
    form=LessonDetailForm,
    fields=['date'],
    extra=0  # No extra forms, only edit existing lesson details
)

def class_detail(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson')
    class_form = ClassUpdateForm(instance=class_instance)
    lesson_form = LessonForm()
    detail_form = LessonDetailForm()
    # Initialize formset for editing lesson dates
    lesson_detail_formset = LessonDetailFormSet(queryset=lesson_details)
    zipped_form_details = zip(lesson_detail_formset.forms, lesson_details)

    if request.method == 'POST':
        action = request.POST.get('action')
        print('POST action:', action)  # Debug
        print('POST data:', request.POST)  # Debug

        if action == 'update_class':
            class_form = ClassUpdateForm(request.POST, instance=class_instance)
            if class_form.is_valid():
                class_form.save()
                return redirect('class_detail', class_id=class_id)

        elif action == 'add_lesson':
            lesson_form = LessonForm(request.POST)
            detail_form = LessonDetailForm(request.POST)
            print('Lesson form valid:', lesson_form.is_valid())  # Debug
            print('Detail form valid:', detail_form.is_valid())  # Debug
            print('Detail form errors:', detail_form.errors)  # Debug
            if lesson_form.is_valid() and detail_form.is_valid():
                new_lesson = lesson_form.save(commit=False)
                new_lesson.course = class_instance.course
                new_lesson.save()

                lesson_detail = detail_form.save(commit=False)
                lesson_detail.lesson = new_lesson
                lesson_detail.classes = class_instance
                lesson_detail.save()

                return redirect('class_detail', class_id=class_id)
            else:
                print('Lesson form errors:', lesson_form.errors)  # Debug
                print('Detail form errors:', detail_form.errors)  # Debug

        elif action == 'update_lesson_dates':
            lesson_detail_formset = LessonDetailFormSet(request.POST, queryset=lesson_details)
            print('Formset valid:', lesson_detail_formset.is_valid())  # Debug
            print('Formset errors:', lesson_detail_formset.errors)  # Debug
            if lesson_detail_formset.is_valid():
                lesson_detail_formset.save()
                messages.success(request, "Cập nhật ngày học thành công!")
                return redirect('class_detail', class_id=class_id)
            else:
                messages.error(request, "Có lỗi khi cập nhật ngày học.")

    return render(request, 'class_detail.html', {
        'class_instance': class_instance,
        'lesson_details': lesson_details,
        'class_form': class_form,
        'lesson_form': lesson_form,
        'detail_form': detail_form,
        'lesson_detail_formset': lesson_detail_formset,
        "zipped_form_details": zipped_form_details,
    })

# ... (rest of the views.py remains unchanged)
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

    # Đúng: Lọc bài học theo khóa học của lớp
    lesson_details = LESSON_DETAIL.objects.filter(
        lesson__course=class_instance.course
    ).select_related('lesson')

    rollcall_data = []
    for lesson_detail in lesson_details:
        rollcall_users = []
        rollcall = getattr(lesson_detail, 'rollcall', None)
        if rollcall:
            rollcall_users = ROLLCALL_USER.objects.filter(
                rollcall=rollcall
            ).select_related('userclass__user')

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
class ClassForm:
    pass


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
