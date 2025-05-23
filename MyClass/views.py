import os

from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from english.models import LESSON, USER_CLASS, LESSON_DETAIL, EXERCISE, SUBMISSION, COURSE
from english.views import is_student

# views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from english.models import LESSON, LESSON_DETAIL, CLASS
from datetime import datetime, timedelta


def get_lesson_details(request, lesson_id, class_id):
    if request.method == "GET":
        # Lấy lesson
        lesson = get_object_or_404(LESSON, lesson_id=lesson_id)

        # Lấy thông tin lớp
        class_obj = get_object_or_404(CLASS, class_id=class_id)

        # Xác định tuần hiện tại (dựa trên ngày hiện tại)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Thứ Hai
        end_of_week = start_of_week + timedelta(days=6)  # Chủ Nhật

        # Lấy tất cả các buổi học (LESSON_DETAIL) có cùng lesson_id trong tuần
        lesson_details = LESSON_DETAIL.objects.filter(
            lesson_id=lesson_id,
            date__range=[start_of_week, end_of_week]
        ).exclude(date__isnull=True).select_related('classes')

        # Chuẩn bị dữ liệu trả về
        lesson_details_data = [
            {
                'lessondetail_id': detail.lessondetail_id,
                'class_name': detail.classes.class_name,
                'date': detail.date.strftime('%Y-%m-%d') if detail.date else 'Chưa xác định',
                'course_name': detail.classes.course.course_name
            }
            for detail in lesson_details
        ]
        # Thông tin lớp
        class_data = {
            'class_id': class_obj.class_id,
            'class_name': class_obj.class_name,
            'course_name': class_obj.course.course_name,
            'begin_time': class_obj.begin_time.strftime('%Y-%m-%d'),
            'end_time': class_obj.end_time.strftime('%Y-%m-%d'),
            'status': class_obj.status
        }

        return JsonResponse({
            'lesson': {
                'lesson_id': lesson.lesson_id,
                'lesson_name': lesson.lesson_name,
                'description': lesson.description
            },
            'class': class_data,
            'lesson_details': lesson_details_data
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)
@login_required
@user_passes_test(is_student)
def student_submission(request, class_id, lesson_id):
    try:
        # Get the lesson and class
        lesson = get_object_or_404(LESSON, pk=lesson_id)
        class_instance = get_object_or_404(CLASS, pk=class_id)

        # Find the user's enrolled class for the specific class_id
        user_class = USER_CLASS.objects.filter(
            user=request.user,
            classes=class_instance
        ).select_related('classes').first()

        if not user_class:
            messages.error(request, 'Bạn chưa được đăng ký vào lớp học này. Vui lòng liên hệ giáo viên.')
            return render(request, 'error.html', {
                'message': 'Bạn chưa được đăng ký vào lớp học này. Vui lòng liên hệ giáo viên.',
                'class_id': class_id
            })
        # Get the lesson detail for the specific class and lesson
        lesson_detail = LESSON_DETAIL.objects.filter(
            lesson=lesson,
            classes=class_instance
        ).select_related('lesson', 'classes').first()

        if not lesson_detail:
            messages.error(request, f'Không tìm thấy thông tin buổi học {lesson.lesson_name} cho lớp {class_instance.class_name}.')
            return render(request, 'error.html', {
                'message': f'Không tìm thấy thông tin buổi học {lesson.lesson_name} cho lớp {class_instance.class_name}. Vui lòng liên hệ giáo viên.',
                'class_id': class_id
            })
        # Get the exercise for the lesson detail
        exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
        if not exercise:
            messages.error(request, f'Không tìm thấy bài tập cho buổi học {lesson.lesson_name}.')
            return render(request, 'error.html', {
                'message': f'Không tìm thấy bài tập cho buổi học {lesson.lesson_name}. Vui lòng liên hệ giáo viên.',
                'class_id': class_id
            })

        course = lesson.course
        submission = SUBMISSION.objects.filter(userclass=user_class, exercise=exercise).first()

        due_date = exercise.duedate
        now = timezone.now().date()

        time_remaining = None
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
        namefile = submission.submission_file_content.name.split('/')[-1] if submission and submission.submission_file_content else None

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
            'submission_file_name': namefile,
            'class_id': class_id,
            'class_name': class_instance.class_name,
        }

        if request.method == 'POST':
            if due_date and now > due_date:
                messages.error(request, 'Đã hết hạn nộp bài!')
                return render(request, 'student_submission.html', context)

            submission_file = request.FILES.get('submission_file')
            if not submission_file:
                messages.error(request, 'Vui lòng chọn tệp để nộp!')
                return render(request, 'student_submission.html', context)

            allowed_types = ['.docx', '.pdf']
            file_ext = submission_file.name.lower().split('.')[-1]
            if f'.{file_ext}' not in allowed_types:
                messages.error(request, 'Chỉ chấp nhận tệp .docx hoặc .pdf!')
                return render(request, 'student_submission.html', context)

            if submission:
                submission.submission_file_content = submission_file
                submission.submit_date = timezone.now()
                submission.status = 'Checking'
                submission.review = None
                submission.save()
            else:
                submission = SUBMISSION.objects.create(
                    userclass=user_class,
                    exercise=exercise,
                    status='Checking',
                    submit_date=timezone.now(),
                    submission_file_content=submission_file
                )

            messages.success(request, 'Nộp bài thành công!')
            return render(request, 'student_submission.html', context)

        return render(request, 'student_submission.html', context)

    except Exception as e:
        messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
        return render(request, 'error.html', {
            'message': f'Đã xảy ra lỗi: {str(e)}. Vui lòng thử lại hoặc liên hệ giáo viên.'
        })
# Các hàm khác (student_homework, download_submission) giữ nguyên như trước
@login_required
@user_passes_test(is_student)
def student_homework(request, class_id):
    # Kiểm tra xem class_id có tồn tại trong bảng CLASS
    class_instance = get_object_or_404(CLASS, class_id=class_id)

    # Kiểm tra xem người dùng có được đăng ký vào lớp học này không
    user_class = USER_CLASS.objects.filter(
        user=request.user,
        classes=class_instance
    ).select_related('classes').first()

    if not user_class:
        messages.error(
            request,
            f'Bạn chưa được đăng ký vào lớp học "{class_instance.class_name}". Vui lòng liên hệ giáo viên.'
        )
        return render(request, 'student_homework.html', {
            'error': f'Bạn chưa được đăng ký vào lớp học "{class_instance.class_name}". Vui lòng liên hệ giáo viên.',
            'page_title': 'Bài tập về nhà'
        })

    # Lấy thông tin khóa học
    course = class_instance.course

    # Lấy danh sách bài tập qua LESSON_DETAIL
    lesson_details = LESSON_DETAIL.objects.filter(
        classes=class_instance
    ).select_related('lesson').order_by('lesson__session_number')

    lesson_data = []
    for lesson_detail in lesson_details:
        lesson = lesson_detail.lesson
        exercise = EXERCISE.objects.filter(lessondetail=lesson_detail).first()
        description = lesson.description.split('Mục tiêu')[0] if 'Mục tiêu' in lesson.description else lesson.description
        lesson_data.append({
            'lesson_id': lesson.lesson_id,
            'lesson_file': lesson.lesson_file if lesson.lesson_file else '#',
            'exercise_file': lesson.exercise_file if lesson.exercise_file else '#',
            'description': description,
            'session_number': lesson.session_number,
            'exercise_id': exercise.exercise_id if exercise else None,
            'due_date': exercise.duedate if exercise else None
        })

    return render(request, 'student_homework.html', {
        'course': course,
        'lessons': lesson_data,
        'page_title': f'Bài tập - {course.course_name}',
        'class_name': class_instance.class_name,
        'class_id': class_id
    })
@login_required
@user_passes_test(is_student)
def download_submission(request, submission_id):
    submission = get_object_or_404(SUBMISSION, pk=submission_id)

    if submission.userclass.user != request.user:
        return HttpResponse("Bạn không có quyền tải tệp này.", status=403)

    if not submission.submission_file_content:
        return HttpResponse("Không tìm thấy tệp để tải.", status=404)

    file_path = submission.submission_file_content.path
    with open(file_path, 'rb') as f:
        file_name = os.path.basename(submission.submission_file_content.name)
        response = HttpResponse(f.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


from django.utils import timezone
from datetime import timedelta


from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from english.models import USER_CLASS, LESSON_DETAIL, EXERCISE, SUBMISSION, COURSE, CLASS

@login_required
def student_class(request):
    # Get all classes the user is enrolled in
    user_classes = USER_CLASS.objects.filter(user=request.user).select_related('classes__course')

    if not user_classes:
        return render(request, 'student_class.html', {
            'error': 'Bạn chưa được đăng ký vào bất kỳ lớp học nào. Vui lòng liên hệ giáo viên.',
            'page_title': 'Lớp học của tôi'
        })

    class_data = []
    for user_class in user_classes:
        class_instance = user_class.classes
        class_data.append({
            'class_id': class_instance.class_id,
            'class_name': class_instance.class_name,
            'course_name': class_instance.course.course_name,
            'begin_time': class_instance.begin_time,
            'end_time': class_instance.end_time,
            'status': class_instance.status,
            'course_id': class_instance.course.course_id,
            'teacher_name': class_instance.course.teacher_name or "Chưa có giáo viên",  # Get from COURSE
        })

    # Fetch assignments due within the next 3 days
    now = timezone.now().date()
    due_date_limit = now + timedelta(days=3)
    upcoming_assignments = []

    for user_class in user_classes:
        lesson_details = LESSON_DETAIL.objects.filter(classes=user_class.classes).select_related('lesson__course')
        for lesson_detail in lesson_details:
            exercises = EXERCISE.objects.filter(
                lessondetail=lesson_detail,
                duedate__gte=now,
                duedate__lte=due_date_limit
            )
            for exercise in exercises:
                lesson = lesson_detail.lesson
                course = lesson.course
                submission = SUBMISSION.objects.filter(
                    userclass=user_class,
                    exercise=exercise
                ).first()
                time_remaining = exercise.duedate - now
                time_remaining_days = time_remaining.days
                time_remaining_text = (
                    f"Còn {time_remaining_days} ngày" if time_remaining_days > 0
                    else "Hôm nay là hạn cuối"
                )
                upcoming_assignments.append({
                    'course_name': course.course_name,
                    'lesson_name': lesson.lesson_name,
                    'exercise_id': exercise.exercise_id,
                    'duedate': exercise.duedate,
                    'time_remaining': time_remaining_text,
                    'submission_status': submission.status if submission else "Chưa nộp",
                    'lesson_id': lesson.lesson_id,
                    'class_id': user_class.classes.class_id,  # Add class_id for submission link
                })

    return render(request, 'student_class.html', {
        'class_data': class_data,
        'page_title': 'Lớp học của tôi',
        'upcoming_assignments': upcoming_assignments,
    })