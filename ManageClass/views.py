import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from english.models import CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL, ROLLCALL_USER, SUBMISSION, EXERCISE,LESSON_DETAIL
from .forms import ClassForm
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
def class_detail(request, class_id):
    # Lấy đối tượng lớp học
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Tính sĩ số: Đếm số lượng học viên trong lớp qua quan hệ USER_CLASS
    class_size = USER_CLASS.objects.filter(classes=class_instance).count()

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_instance)
        if form.is_valid():
            form.save()
            return redirect('class_detail', class_id=class_instance.pk)
    else:
        form = ClassForm(instance=class_instance)

    return render(request, 'class_detail.html', {
        'form': form,
        'class_instance': class_instance,
        'class_size': class_size  # Truyền sĩ số vào context
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


from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from english.models import ROLLCALL, USER_CLASS


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from english.models import ROLLCALL, ROLLCALL_USER, LESSON_DETAIL


def update_rollcall(request):
    if request.method == 'POST':
        rollcall_data = request.POST.get('rollcall_data')

        if rollcall_data:
            try:
                # Chuyển chuỗi JSON thành từ điển Python
                rollcall_data = json.loads(rollcall_data)

                # Cập nhật trạng thái điểm danh cho từng user
                for user_id, data in rollcall_data.items():
                    # Thay đổi query để lấy RollCallUser đúng
                    user = ROLLCALL_USER.objects.get(
                        userclass__user__id=user_id,
                        lesson_detail__id=data['lesson_detail_id']
                    )
                    user.status = data['status']
                    user.save()

                return JsonResponse({'message': 'Cập nhật trạng thái thành công!'})

            except Exception as e:
                return JsonResponse({'message': f'Error: {str(e)}'}, status=400)

        return JsonResponse({'message': 'Dữ liệu không hợp lệ'}, status=400)
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
