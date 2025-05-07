from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from english.models import COURSE, LESSON, EXERCISE, LESSON_DETAIL, SUBMISSION, USER_CLASS, CLASS

@login_required
def student_submission(request, lesson_id):
    lesson = get_object_or_404(LESSON, pk=lesson_id)
    user_class = USER_CLASS.objects.filter(user=request.user).first()

    if not user_class:
        return render(request, 'error.html', {
            'message': 'Bạn chưa được đăng ký vào bất kỳ lớp học nào. Vui lòng liên hệ giáo viên.'
        })

    lesson_detail = LESSON_DETAIL.objects.filter(lesson=lesson, classes=user_class.classes).first()
    if not lesson_detail:
        return render(request, 'error.html', {
            'message': f'Không tìm thấy thông tin buổi học {lesson_id} cho lớp của bạn. Vui lòng liên hệ giáo viên.'
        })

    exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
    if not exercise:
        return render(request, 'error.html', {
            'message': f'Không tìm thấy bài tập cho buổi học {lesson_id}. Vui lòng liên hệ giáo viên.'
        })

    course = lesson.course
    submission = SUBMISSION.objects.filter(userclass=user_class, exercise=exercise).first()

    # Tính toán thời hạn và trạng thái với datetime.datetime
    due_date = exercise.duedate  # Đã là datetime.datetime từ DateTimeField
    now = timezone.now()  # Lấy thời gian hiện tại bao gồm ngày và giờ

    if due_date:
        time_remaining = due_date - now
        time_remaining_days = time_remaining.days
        if time_remaining_days > 0:
            time_remaining = f"Còn {time_remaining_days} ngày"
        elif time_remaining_days == 0:
            time_remaining = "Hôm nay là hạn cuối"
        else:
            time_remaining = "Đã hết hạn"
    else:
        time_remaining = "Không có hạn nộp"

    submission_status = submission.status if submission else "Chưa nộp"
    grading_status = submission.review if submission and submission.review else "Chưa chấm"
    last_edit = submission.submit_date if submission else "Chưa nộp"

    if request.method == 'POST':
        if due_date and now > due_date:
            messages.error(request, 'Đã hết hạn nộp bài!')
            return render(request, 'student_submission.html', {
                'lesson': lesson,
                'course': course,
                'exercise': exercise,
                'due_date': due_date,
                'time_remaining': time_remaining,
                'submission_status': submission_status,
                'grading_status': grading_status,
                'last_edit': last_edit,
                'submission': submission,
            })

        submission_file = request.FILES.get('submission_file')
        if not submission_file:
            messages.error(request, 'Vui lòng chọn tệp để nộp!')
            return render(request, 'student_submission.html', {
                'lesson': lesson,
                'course': course,
                'exercise': exercise,
                'due_date': due_date,
                'time_remaining': time_remaining,
                'submission_status': submission_status,
                'grading_status': grading_status,
                'last_edit': last_edit,
                'submission': submission,
            })

        allowed_types = ['.docx', '.pdf']
        file_ext = submission_file.name.lower().split('.')[-1]
        if f'.{file_ext}' not in allowed_types:
            messages.error(request, 'Chỉ chấp nhận tệp .docx hoặc .pdf!')
            return render(request, 'student_submission.html', {
                'lesson': lesson,
                'course': course,
                'exercise': exercise,
                'due_date': due_date,
                'time_remaining': time_remaining,
                'submission_status': submission_status,
                'grading_status': grading_status,
                'last_edit': last_edit,
                'submission': submission,
            })

        # Đọc nội dung tệp dưới dạng nhị phân
        file_content = submission_file.read()
        file_name = submission_file.name
        file_type = f'.{file_ext}'

        if submission:
            submission.submission_file_content = file_content
            submission.submission_file_name = file_name
            submission.submission_file_type = file_type
            submission.submit_date = timezone.now()
            submission.status = 'done'
            submission.review = None
            submission.save()
        else:
            submission = SUBMISSION.objects.create(
                userclass=user_class,
                exercise=exercise,
                status='done',
                submit_date=timezone.now(),
                submission_file_content=file_content,
                submission_file_name=file_name,
                submission_file_type=file_type
            )

        messages.success(request, 'Nộp bài thành công!')
        return HttpResponseRedirect(reverse('student_submission', args=[lesson_id]))

    context = {
        'lesson': lesson,
        'course': course,
        'exercise': exercise,
        'due_date': due_date,
        'time_remaining': time_remaining,
        'submission_status': submission_status,
        'grading_status': grading_status,
        'last_edit': last_edit,
        'submission': submission,
    }

    return render(request, 'student_submission.html', context)

# Các hàm khác (student_homework, download_submission) giữ nguyên như trước
@login_required
def student_homework(request):
    # Get the user's enrolled classes
    user_classes = USER_CLASS.objects.filter(user=request.user)

    if not user_classes:
        return render(request, 'student_homework.html', {
            'error': 'Bạn chưa được đăng ký vào bất kỳ lớp học nào. Vui lòng liên hệ giáo viên.',
            'page_title': 'Bài tập về nhà'
        })

    # Get unique courses from the user's classes
    courses = COURSE.objects.filter(class__user_class__user=request.user).distinct()

    if not courses:
        return render(request, 'student_homework.html', {
            'error': 'Không tìm thấy khóa học nào cho bạn. Vui lòng liên hệ giáo viên.',
            'page_title': 'Bài tập về nhà'
        })

    # Assuming the user is typically enrolled in one course, take the first one
    course = courses.first()

    # Get lessons for the course
    lessons = LESSON.objects.filter(course=course).order_by('lesson_id')

    lesson_data = []
    for lesson in lessons:
        lesson_data.append({
            'lesson_id': lesson.lesson_id,
            'lesson_file': lesson.lesson_file if lesson.lesson_file else '#',  # Sử dụng trực tiếp giá trị URL
            'exercise_file': lesson.exercise_file if lesson.exercise_file else '#',  # Sử dụng trực tiếp giá trị URL
        })

    return render(request, 'student_homework.html', {
        'course': course,
        'lessons': lesson_data,
        'page_title': f'Bài tập - {course.course_name}'
    })

@login_required
def download_submission(request, submission_id):
    submission = get_object_or_404(SUBMISSION, pk=submission_id)

    if submission.userclass.user != request.user:
        return HttpResponse("Bạn không có quyền tải tệp này.", status=403)

    response = HttpResponse(
        submission.submission_file_content,
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{submission.submission_file_name}"'
    return response