from django.shortcuts import render, get_object_or_404


from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from english.models import COURSE, LESSON, EXERCISE, LESSON_DETAIL

def student_submission(request, lesson_id):
    # # Lấy khóa học và bài học
    # course = get_object_or_404(Course, pk=1)
    # lesson = get_object_or_404(Lesson, course=course, lesson_id=lesson_id)
    #
    # # Lấy bài tập liên quan đến bài học
    # exercise = Exercise.objects.filter(lesson_id=lesson.lesson_detail_id).first()

    # Lấy bài học và kiểm tra tồn tại
    lesson = get_object_or_404(LESSON, pk=lesson_id)
    course = lesson.course  # Lấy course từ lesson

    # Lấy LessonDetail đầu tiên liên quan đến lesson (nếu có nhiều class)
    lesson_detail = LESSON_DETAIL.objects.filter(lesson=lesson).first()

    if not lesson_detail:
        return render(request, 'error.html', {'message': 'Chi tiết bài học chưa được cấu hình.'})

    # Lấy bài tập liên quan đến LessonDetail
    exercise = EXERCISE.objects.filter(lesson_detail=lesson_detail).first()
    if not exercise:
        return render(request, 'error.html', {'message': 'Bài tập cho bài học này chưa được tạo.'})

    # Tính thời gian còn lại
    due_date = exercise.duedate
    today = timezone.now().date()
    time_remaining = (due_date - today).days

    # Định dạng ngày đẹp
    months = {
        1: 'Tháng một', 2: 'Tháng hai', 3: 'Tháng ba', 4: 'Tháng tư',
        5: 'Tháng năm', 6: 'Tháng sáu', 7: 'Tháng bảy', 8: 'Tháng tám',
        9: 'Tháng chín', 10: 'Tháng mười', 11: 'Tháng mười một', 12: 'Tháng mười hai'
    }

    weekdays = {
        0: 'Thứ hai', 1: 'Thứ ba', 2: 'Thứ tư', 3: 'Thứ năm',
        4: 'Thứ sáu', 5: 'Thứ bảy', 6: 'Chủ nhật'
    }

    weekday = weekdays[due_date.weekday()]
    month = months[due_date.month]
    formatted_due_date = f"{weekday}, {due_date.day} {month} {due_date.year}, 23:59 PM"

    context = {
        'course': course,
        'lesson': lesson,
        'exercise': exercise,
        'due_date': formatted_due_date,
        'time_remaining': f"{time_remaining} ngày" if time_remaining > 0 else "Đã hết hạn",
        'submission_status': "No attempt",  # Mặc định chưa nộp
        'grading_status': "Chưa chấm điểm",  # Mặc định chưa chấm
        'last_edit': "-",
    }

    return render(request, 'student_submission.html', context)


def student_homework(request):
    # Lấy khóa học theo course_id
    course = get_object_or_404(COURSE, pk=1)

    # Lấy tất cả các bài học thuộc khóa học này
    lessons = LESSON.objects.filter(course=course).order_by('lesson_id')

    # Chuẩn bị dữ liệu đơn giản cho template
    lesson_data = []
    for lesson in lessons:
        lesson_data.append({
            'lesson_id': lesson.lesson_id,
            'material': f"Tài liệu học buổi {lesson.lesson_id}",
            'homework': f"Bài tập buổi {lesson.lesson_id}",
            'submit': f"Nộp bài tập buổi {lesson.lesson_id}",
        })

    return render(request, 'student_homework.html', {
        'course': course,
        'lessons': lesson_data,
        'page_title': f'Bài tập - {course.course_name}'
    })
# # views.py
# from django.shortcuts import render
# from english.models import Lesson, Course
#
#
# def MyClass(request,course_id):
#     # Lấy danh sách bài học từ cơ sở dữ liệu
#     course = Course.objects.get(course_id=course_id)
#     lessons = Lesson.objects.filter(course=course)
#     # lesson_data = []
#     # for lesson in lessons:
#     #     # Lấy tài liệu học cho bài học
#     #     documents = Document.objects.filter(lesson=lesson)
#     #     # Lấy bài tập cho bài học
#     #     exercises = Exercise.objects.filter(lesson=lesson)
#     #     # Lấy trạng thái nộp bài cho người dùng (nếu có)
#     #     submissions = Submission.objects.filter(user=request.user, exercise__lesson=lesson)
#     #     is_submitted = submissions.exists()
#     #
#     #     lesson_data.append({
#     #         'lesson': lesson,
#     #         'documents': documents,
#     #         'exercises': exercises,
#     #         'is_submitted': is_submitted
#     #     })
#
#     # Truyền dữ liệu vào context để hiển thị trong template
#     return render(request, 'MyClass.html', {'lessons': lessons,'course':course})


# from django.shortcuts import render, get_object_or_404, redirect
# # from django.contrib.auth.decorators import login_required
# from django.utils import timezone
# from datetime import timedelta
# from english.models import (
#     Course, Lesson, LessonDetail, Exercise, Submission,
#     UserProfile, UserClass, Class
# )
#
# # @login_required  # Commented out
# def student_submission(request, lesson_id):
#     # Get the course (assuming course_id=1 as in your previous view)
#     course = get_object_or_404(Course, pk=1)
#
#     # Get the specific lesson
#     lesson = get_object_or_404(Lesson, course=course, lesson_id=lesson_id)
#
#     # Get the user profile for the current user
#     # user_profile = get_object_or_404(UserProfile, account=request.user.account)
#
#     # Get the user's class for this course
#     user_class = UserClass.objects.filter(
#         # user=user_profile,
#         class_instance__course=course
#     ).first()
#
#     if not user_class:
#         # Handle case where user is not enrolled in this course
#         return render(request, 'error.html', {'message': 'Bạn chưa đăng ký khóa học này.'})
#
#     # Get the lesson detail for this lesson and class
#     lesson_detail = LessonDetail.objects.filter(
#         lesson=lesson,
#         class_instance=user_class.class_instance
#     ).first()
#
#     if not lesson_detail:
#         # Handle case where lesson detail doesn't exist
#         return render(request, 'error.html', {'message': 'Bài học này chưa được cấu hình cho lớp của bạn.'})
#
#     # Get exercise for this lesson detail
#     exercise = Exercise.objects.filter(lesson_detail=lesson_detail).first()
#
#     if not exercise:
#         # Handle case where exercise doesn't exist
#         return render(request, 'error.html', {'message': 'Bài tập cho bài học này chưa được tạo.'})
#
#     # Get submission for this user and exercise
#     submission = Submission.objects.filter(
#         user=user_profile,
#         exercise=exercise
#     ).first()
#
#     # Calculate time remaining
#     due_date = exercise.duedate
#     today = timezone.now().date()
#     time_remaining = (due_date - today).days
#
#     # Format the due date in Vietnamese
#     months = {
#         1: 'Tháng một', 2: 'Tháng hai', 3: 'Tháng ba', 4: 'Tháng tư',
#         5: 'Tháng năm', 6: 'Tháng sáu', 7: 'Tháng bảy', 8: 'Tháng tám',
#         9: 'Tháng chín', 10: 'Tháng mười', 11: 'Tháng mười một', 12: 'Tháng mười hai'
#     }
#
#     weekdays = {
#         0: 'Thứ hai', 1: 'Thứ ba', 2: 'Thứ tư', 3: 'Thứ năm',
#         4: 'Thứ sáu', 5: 'Thứ bảy', 6: 'Chủ nhật'
#     }
#
#     weekday = weekdays[due_date.weekday()]
#     month = months[due_date.month]
#     formatted_due_date = f"{weekday}, {due_date.day} {month} {due_date.year}, 23:59 PM"
#
#     # Determine submission status
#     if submission:
#         submission_status = "Submitted"
#         grading_status = "Chấm điểm" if submission.status == 'check' else "Chưa chấm điểm"
#         last_edit = submission.submit_date.strftime("%d/%m/%Y") if submission.submit_date else "-"
#     else:
#         submission_status = "No attempt"
#         grading_status = "Chấm điểm"  # Default status as shown in the image
#         last_edit = "-"
#
#     context = {
#         'course': course,
#         'lesson': lesson,
#         'exercise': exercise,
#         'submission': submission,
#         'due_date': formatted_due_date,
#         'time_remaining': f"{time_remaining} ngày" if time_remaining > 0 else "Đã hết hạn",
#         'submission_status': submission_status,
#         'grading_status': grading_status,
#         'last_edit': last_edit,
#         'comments_count': 0,  # You can implement comment counting if needed
#         'user_profile': user_profile,
#     }
#
#     return render(request, 'student_submission.html', context)