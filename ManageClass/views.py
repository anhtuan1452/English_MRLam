from django.shortcuts import render, get_object_or_404, redirect
from english.models import CLASS, USER_CLASS, USER_PROFILE, COURSE, ROLLCALL, ROLLCALL_USER
from .forms import ClassForm  # Form tạo lớp học
from django.contrib.auth.models import User

def class_list(request):
    classes = CLASS.objects.select_related('course').all()
    return render(request, 'class_list.html', {'classes': classes})


def class_detail(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)
    user_classes = USER_CLASS.objects.filter(classes=class_instance).select_related('user')

    return render(request, 'class_detail.html', {
        'class_instance': class_instance,
        'user_classes': user_classes
    })


def class_rollcall(request, class_id):
    class_instance = get_object_or_404(CLASS, pk=class_id)

    # Lấy tất cả buổi học (LessonDetail) của lớp này
    lessons = class_instance.lessondetail_set.all().prefetch_related('rollcall')

    rollcall_data = []
    for lesson in lessons:
        try:
            rollcall = lesson.rollcall  # one-to-one, có thể gây lỗi nếu chưa tồn tại
            rollcall_users = ROLLCALL_USER.objects.filter(rollcall=rollcall).select_related('userclass__user')
            rollcall_data.append({
                'lesson': lesson,
                'rollcall_users': rollcall_users
            })
        except ROLLCALL.DoesNotExist:
            continue

    return render(request, 'class_rollcall.html', {
        'class_instance': class_instance,
        'rollcall_data': rollcall_data
    })


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


def add_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('class_list')
    else:
        form = ClassForm()
    return render(request, 'add_class.html', {'form': form})
from django.utils.timezone import now  # dùng timezone-aware datetime

def class_list(request):
    query = request.GET.get("q", "")
    classes = CLASS.objects.all()
    if query:
        classes = classes.filter(class_name__icontains=query)
    return render(request, "class_list.html", {"classes": classes})

