import csv
import os
import django
from datetime import datetime

# Cấu hình Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'English_MRLam.settings')  # Thay 'your_project_name' bằng tên project của bạn
django.setup()

from english.models import LESSON, LESSON_DETAIL, EXERCISE, COURSE, CLASS

# Xóa dữ liệu cũ
LESSON.objects.all().delete()
LESSON_DETAIL.objects.all().delete()
EXERCISE.objects.all().delete()

# Đọc và thêm dữ liệu mới cho LESSON
with open('LESSON.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        course = COURSE.objects.get(course_id=int(row['course_id']))
        LESSON.objects.create(
            lesson_id=int(row['lesson_id']),
            lesson_file=row['lesson_file'],
            exercise_file=row['exercise_file'],
            course=course,
            lesson_name=row['lesson_name'],
            description=row['description'] if row['description'] else None
        )

# Đọc và thêm dữ liệu mới cho LESSON_DETAIL
with open('LessonDetail.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        lesson = LESSON.objects.get(lesson_id=int(row['lesson_id']))
        classes = CLASS.objects.get(class_id=int(row['classes_id']))
        LESSON_DETAIL.objects.create(
            lessondetail_id=int(row['lessondetail_id']),
            lesson=lesson,
            classes=classes,
            session_number=row['session_number']
        )

# Đọc và thêm dữ liệu mới cho EXERCISE
with open('EXERCISE.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        lessondetail = LESSON_DETAIL.objects.get(lessondetail_id=int(row['lessondetail_id']))
        # Sử dụng định dạng đúng cho datetime: YYYY-MM-DD HH:MM:SS
        duedate = datetime.strptime(row['duedate'], '%Y-%m-%d %H:%M:%S')
        EXERCISE.objects.create(
            exercise_id=int(row['exercise_id']),
            lessondetail=lessondetail,
            duedate=duedate
        )

print("Dữ liệu đã được thêm thành công vào cơ sở dữ liệu!")