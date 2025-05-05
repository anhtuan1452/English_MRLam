import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from english.models import CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL, ROLLCALL_USER, SUBMISSION, EXERCISE,LESSON_DETAIL

from django.contrib.auth.models import User
from django.utils.timezone import now
from django.db.models import Count

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

# Chi tiết lớp học - Tab "Mô tả lớp học"
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory

from english.models import CLASS, LESSON_DETAIL, LESSON
from course_admin.forms import LessonDetailFormSet

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from english.models import CLASS, LESSON_DETAIL, COURSE
from .forms import LessonDetailForm, ClassForm


def class_detail(request, class_id):
    # Lấy thông tin lớp học từ class_id
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Lấy danh sách các buổi học của lớp
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_lesson':  # Khi nhấn nút thêm buổi học
            form = LessonDetailForm(request.POST)
            if form.is_valid():
                # Lấy thông tin từ form
                lesson_name = form.cleaned_data['lesson_name']
                description = form.cleaned_data['description']
                session_number = form.cleaned_data['session_number']

                # Tạo mới Lesson và LessonDetail
                lesson = LESSON.objects.create(
                    lesson_name=lesson_name,
                    description=description,
                    course=class_instance.course
                )

                LESSON_DETAIL.objects.create(
                    lesson=lesson,
                    classes=class_instance,
                    session_number=session_number
                )

                messages.success(request, "Thêm buổi học thành công!")
                return redirect('class_detail', class_id=class_instance.pk)

            else:
                messages.error(request, "Có lỗi khi thêm buổi học.")
        else:
            # Xử lý các form khác nếu cần
            pass

    else:
        # Form thêm buổi học
        form = LessonDetailForm()

    return render(request, 'class_detail.html', {
        'class_instance': class_instance,
        'lesson_details': lesson_details,
        'form': form
    })


def class_exercise(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Lấy danh sách tất cả các bài nộp của học viên trong lớp này
    submissions = SUBMISSION.objects.filter(
        userclass__classes=class_instance
    ).select_related(
        'userclass__user', 'exercise__lessondetail__lesson'
    )

    # Kiểm tra nếu không có bài nộp nào
    if not submissions:
        submissions = None  # Hoặc bạn có thể hiển thị một thông báo nào đó

    return render(request, 'class_exercise.html', {
        'class_instance': class_instance,
        'class_id': class_id,
        'submissions': submissions
    })

from django.shortcuts import render, get_object_or_404
from english.models import LESSON_DETAIL, ROLLCALL_USER, ROLLCALL
from django.db.models import Count

def class_rollcall(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Truy xuất tất cả các buổi học của lớp
    lesson_details = LESSON_DETAIL.objects.filter(classes=class_instance).select_related('lesson')

    rollcall_data = []
    for lesson_detail in lesson_details:
        rollcall_users = []
        try:
            # Lấy đối tượng rollcall của lesson_detail
            rollcall = lesson_detail.rollcall  # Lấy ROLLCALL liên kết với LESSON_DETAIL
            if rollcall:
                # Lấy danh sách học viên tham gia điểm danh trong buổi học này
                rollcall_users = ROLLCALL_USER.objects.filter(rollcall=rollcall).select_related('userclass__user')
        except ROLLCALL.DoesNotExist:
            rollcall = None  # Không có điểm danh cho buổi học này

        # Lưu dữ liệu điểm danh vào list để render trong template
        rollcall_data.append({
            'lesson_detail': lesson_detail,
            'rollcall_users': rollcall_users,
            'has_rollcall': rollcall is not None,  # Kiểm tra có điểm danh hay không
        })

    return render(request, 'class_rollcall.html', {
        'class_instance': class_instance,
        'rollcall_data': rollcall_data,
    })


# Thêm học viên vào lớp học
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

# Thêm lớp học mới
def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})


from english.models import ROLLCALL, USER_CLASS


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from english.models import ROLLCALL, ROLLCALL_USER, LESSON_DETAIL


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from english.models import ROLLCALL_USER, LESSON_DETAIL

@csrf_exempt  # (nếu dùng POST từ JS mà không có CSRF token)
def update_rollcall(request):
    if request.method == 'POST':
        rollcall_data = request.POST.get('rollcall_data')

        if rollcall_data:
            try:
                rollcall_data = json.loads(rollcall_data)

                for user_id, data in rollcall_data.items():
                    lesson_detail_id = data.get('lesson_detail_id')
                    status = data.get('status')

                    # Kiểm tra lesson_detail_id hợp lệ
                    if not lesson_detail_id or not str(lesson_detail_id).isdigit():
                        continue  # Bỏ qua nếu thiếu hoặc sai kiểu

                    try:
                        lesson_detail = LESSON_DETAIL.objects.get(pk=lesson_detail_id)
                    except LESSON_DETAIL.DoesNotExist:
                        continue  # Bỏ qua nếu không tồn tại

                    try:
                        user = ROLLCALL_USER.objects.get(
                            userclass__user__id=user_id,
                            rollcall__lessondetail=lesson_detail
                        )
                        user.status = status
                        user.save()
                    except ROLLCALL_USER.DoesNotExist:
                        continue  # Không có bản ghi, có thể log nếu cần

                return JsonResponse({'message': 'Cập nhật trạng thái thành công!'})

            except Exception as e:
                return JsonResponse({'message': f'Lỗi xử lý dữ liệu: {str(e)}'}, status=400)

        return JsonResponse({'message': 'Dữ liệu gửi lên không hợp lệ'}, status=400)

    return JsonResponse({'message': 'Chỉ chấp nhận phương thức POST'}, status=405)


def exercise_detail_view(request, class_id, exercise_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    exercise = get_object_or_404(EXERCISE, pk=exercise_id)

    # Lấy tất cả các bài nộp của học viên trong lớp cho bài tập này
    submissions = SUBMISSION.objects.filter(
        exercise=exercise,
        userclass__classes=class_instance
    ).select_related('userclass__user')

    return render(request, 'exercise_detail.html', {
        'class_instance': class_instance,
        'exercise': exercise,
        'submissions': submissions,
    })
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.forms import modelformset_factory

from english.models import COURSE, CLASS, LESSON, LESSON_DETAIL
from course_admin.forms import LessonDetailFormSet
from django.contrib.auth.models import User

def add_lesson_details(request, course_id):
    course = get_object_or_404(COURSE, pk=course_id)

    # Kiểm tra xem khóa học có lớp học mặc định hay không
    default_class = CLASS.objects.filter(course=course).first()
    if not default_class:
        messages.error(request, "Chưa có lớp học cho khóa học này.")
        return redirect('admin_xemkhoahoc', course_id=course.pk)

    if request.method == 'POST':
        formset = LessonDetailFormSet(request.POST)

        if formset.is_valid():
            with transaction.atomic():
                # Lưu tất cả các buổi học vào cơ sở dữ liệu
                for form in formset:
                    lesson = form.cleaned_data.get('lesson')
                    session_number = form.cleaned_data.get('session_number')
                    date = form.cleaned_data.get('date')

                    if lesson:
                        # Tạo LESSON_DETAIL cho mỗi buổi học
                        LESSON_DETAIL.objects.create(
                            lesson=lesson,
                            classes=default_class,
                            session_number=session_number,
                            date=date
                        )

                messages.success(request, "Thêm buổi học thành công!")
                return redirect('admin_xemkhoahoc', course_id=course.pk)
        else:
            messages.error(request, "Có lỗi xảy ra khi thêm buổi học.")

    else:
        # Khởi tạo formset trống để người dùng nhập các buổi học mới
        formset = LessonDetailFormSet(queryset=LESSON_DETAIL.objects.none())

    return render(request, 'lesson_details.html', {
        'formset': formset,
        'course': course,
    })
