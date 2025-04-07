# views.py
from django.shortcuts import render
from english.models import Lesson, Course


def myclass(request,course_id):
    # Lấy danh sách bài học từ cơ sở dữ liệu
    course = Course.objects.get(course_id=course_id)
    lessons = Lesson.objects.filter(course=course)
    # lesson_data = []
    # for lesson in lessons:
    #     # Lấy tài liệu học cho bài học
    #     documents = Document.objects.filter(lesson=lesson)
    #     # Lấy bài tập cho bài học
    #     exercises = Exercise.objects.filter(lesson=lesson)
    #     # Lấy trạng thái nộp bài cho người dùng (nếu có)
    #     submissions = Submission.objects.filter(user=request.user, exercise__lesson=lesson)
    #     is_submitted = submissions.exists()
    #
    #     lesson_data.append({
    #         'lesson': lesson,
    #         'documents': documents,
    #         'exercises': exercises,
    #         'is_submitted': is_submitted
    #     })

    # Truyền dữ liệu vào context để hiển thị trong template
    return render(request, 'myclass.html', {'lessons': lessons,'course':course})
