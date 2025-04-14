from django.shortcuts import render, get_object_or_404, redirect
from english.models import CLASS, USER_CLASS, COURSE, ROLLCALL, ROLLCALL_USER, LESSON_DETAIL, LESSON, SUBMISSION, EXERCISE
from .forms import ClassForm

def class_list(request):
    classes = CLASS.objects.all()
    return render(request, 'class_list.html', {'classes': classes})

def class_detail(request, class_id):
    classroom = get_object_or_404(CLASS, class_id=class_id)
    return render(request, 'class_detail.html', {'classroom': classroom})

def add_student_to_class(request, class_id):
    # logic thêm học sinh vào lớp
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

def class_rollcall(request, class_id):
    classroom = get_object_or_404(Class, class_id=class_id)
    lessons = LessonDetail.objects.filter(class_instance=classroom).order_by('lesson_name')
    students = UserClass.objects.filter(class_instance=classroom)

    if request.method == "POST":
        lesson_id = request.POST.get("lesson_id")
        present_ids = request.POST.getlist("present")

        lesson_detail = get_object_or_404(LessonDetail, lessonDetail_id=lesson_id)
        rollcall, created = RollCall.objects.get_or_create(lesson_detail=lesson_detail)

        # Xóa dữ liệu cũ
        RollCallUser.objects.filter(rollcall=rollcall).delete()

        for student in students:
            is_present = str(student.user.user_id) in present_ids
            RollCallUser.objects.create(rollcall=rollcall, userclass=student)

        return redirect('class_rollcall', class_id=class_id)

    return render(request, 'class_rollcall.html', {
        'classroom': classroom,
        'lessons': lessons,
        'students': students,
    })

def class_exercise(request, class_id):
    classroom = get_object_or_404(Class, class_id=class_id)

    # Lấy bài nộp theo lớp học
    submissions = Submission.objects.filter(
        exercise__lesson_detail__class_instance=classroom
    ).select_related('user', 'exercise__lesson_detail').distinct()

    # Lấy bài học của lớp
    lessons = Lesson.objects.filter(
        lessondetail__class_instance=classroom
    ).distinct()

    return render(request, 'class_exercise.html', {
        'classroom': classroom,
        'submissions': submissions,
        'lessons': lessons,
    })
