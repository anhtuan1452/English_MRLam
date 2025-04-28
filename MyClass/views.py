from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from english.models import COURSE, LESSON, EXERCISE, LESSON_DETAIL, SUBMISSION, USER_CLASS
from django.http import HttpResponseRedirect
from django.urls import reverse


@login_required
def student_homework(request):
    course = get_object_or_404(COURSE, pk=3)
    lessons = LESSON.objects.filter(course=course).order_by('lesson_id')

    lesson_data = []
    for lesson in lessons:
        lesson_data.append({
            'lesson_id': lesson.lesson_id,
            'lesson_file': lesson.lesson_file.url if lesson.lesson_file else '#',
            'exercise_file': lesson.exercise_file.url if lesson.exercise_file else '#',
        })

    return render(request, 'student_homework.html', {
        'course': course,
        'lessons': lesson_data,
        'page_title': f'Bài tập - {course.course_name}'
    })


@login_required
def student_submission(request, lesson_id):
    lesson = get_object_or_404(LESSON, pk=lesson_id)
    course = lesson.course

    lesson_detail = LESSON_DETAIL.objects.filter(lesson_id=lesson.lesson_id).first()
    if not lesson_detail:
        return render(request, 'error.html', {'message': 'Chi tiết bài học chưa được cấu hình.'})

    exercise = EXERCISE.objects.filter(lessondetail_id=lesson_detail.lessondetail_id).first()
    if not exercise:
        return render(request, 'error.html', {'message': 'Bài tập cho bài học này chưa được tạo.'})

    user_class = USER_CLASS.objects.filter(user=request.user, classes=lesson_detail.classes).first()
    if not user_class:
        return render(request, 'error.html', {'message': 'Bạn không được đăng ký trong lớp này.'})

    # Ngày hết hạn
    due_date = exercise.duedate
    today = timezone.now().date()

    months = {
        1: 'Tháng một', 2: 'Tháng hai', 3: 'Tháng ba', 4: 'Tháng tư',
        5: 'Tháng năm', 6: 'Tháng sáu', 7: 'Tháng bảy', 8: 'Tháng tám',
        9: 'Tháng chín', 10: 'Tháng mười', 11: 'Tháng mười một', 12: 'Tháng mười hai'
    }
    weekdays = {
        0: 'Thứ hai', 1: 'Thứ ba', 2: 'Thứ tư', 3: 'Thứ năm',
        4: 'Thứ sáu', 5: 'Thứ bảy', 6: 'Chủ nhật'
    }

    if due_date:
        time_remaining = (due_date - today).days
        formatted_due_date = f"{weekdays[due_date.weekday()]}, {due_date.day} {months[due_date.month]} {due_date.year}, 23:59"
    else:
        time_remaining = 0
        formatted_due_date = "Chưa có hạn nộp"

    # Check bài đã nộp chưa
    submission = SUBMISSION.objects.filter(userclass=user_class, exercise=exercise).first()

    if submission and submission.submit_date:
        last_edit = submission.submit_date.strftime("%d/%m/%Y %H:%M")
        submission_status = "Đã nộp"
        grading_status = submission.review if submission.review else "Chưa chấm điểm"
    else:
        last_edit = "-"
        submission_status = "Chưa nộp"
        grading_status = "Chưa chấm điểm"

    # Xử lý khi user bấm Submit bài
    if request.method == 'POST':
        if due_date and today > due_date:
            return render(request, 'error.html', {'message': 'Đã hết hạn nộp bài! Không thể nộp nữa.'})

        submission_file = request.FILES.get('submission_file')
        if submission_file:
            if submission:
                # Update submission cũ
                submission.status = 'done'
                submission.submit_date = timezone.now()
                submission.save()
            else:
                # Tạo mới submission
                submission = SUBMISSION.objects.create(
                    userclass=user_class,
                    exercise=exercise,
                    status='done',
                    submit_date=timezone.now()
                )
            # (Nếu muốn lưu file submission_file, phải thêm field FileField vào SUBMISSION model nhé)

            return HttpResponseRedirect(reverse('student_submission', args=[lesson_id]))

    context = {
        'course': course,
        'lesson': lesson,
        'exercise': exercise,
        'due_date': formatted_due_date,
        'time_remaining': f"{time_remaining} ngày" if time_remaining > 0 else "Đã hết hạn",
        'submission_status': submission_status,
        'grading_status': grading_status,
        'last_edit': last_edit,
        'time_remaining_days': time_remaining,  # để bên HTML disable nút submit nếu cần
    }

    return render(request, 'student_submission.html', context)