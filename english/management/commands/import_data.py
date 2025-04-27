import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from english.models import (
    USER_PROFILE, TEST, QUESTION_MEDIA, QUESTION, RESULT, DOCUMENT,
    COURSE, PAYMENT, PAYMENT_INFO, CLASS, USER_CLASS, LESSON,
    LESSON_DETAIL, EXERCISE, SUBMISSION, ROLLCALL, ROLLCALL_USER
)
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = 'Import data from data.csv into the SQLite3 database'

    def handle(self, *args, **kwargs):
        # Path to data.csv (adjust as needed)
        import os
        import sys
        from pathlib import Path

        # Lấy thư mục chứa file import_data.py (thư mục commands)
        BASE_DIR = Path(__file__).resolve().parent  # Chỉ đi lên 1 thư mục, trỏ đến thư mục commands
        csv_file = os.path.join(BASE_DIR, 'data.csv')  # Trỏ trực tiếp đến data.csv trong thư mục commands

        # Dictionary to store parsed CSV sections
        sections = {}
        current_section = None

        # Read and parse the CSV file
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Check for section headers (e.g., "content: USER")
                for key in row:
                    if key.startswith('content:'):
                        current_section = key.replace('content: ', '')
                        sections[current_section] = []
                        break
                else:
                    if current_section:
                        sections[current_section].append(row)

        # Clear existing data (optional, comment out if you want to append)
        self.stdout.write(self.style.WARNING('Clearing existing data...'))
        USER_PROFILE.objects.all().delete()
        TEST.objects.all().delete()
        QUESTION_MEDIA.objects.all().delete()
        QUESTION.objects.all().delete()
        RESULT.objects.all().delete()
        DOCUMENT.objects.all().delete()
        COURSE.objects.all().delete()
        PAYMENT.objects.all().delete()
        PAYMENT_INFO.objects.all().delete()
        CLASS.objects.all().delete()
        USER_CLASS.objects.all().delete()
        LESSON.objects.all().delete()
        LESSON_DETAIL.objects.all().delete()
        EXERCISE.objects.all().delete()
        SUBMISSION.objects.all().delete()
        ROLLCALL.objects.all().delete()
        ROLLCALL_USER.objects.all().delete()
        User.objects.all().delete()

        # Import USER
        self.stdout.write('Importing USER...')
        user_map = {}
        for row in sections.get('USER', []):
            if row['id']:  # Skip empty rows
                user = User(
                    id=int(row['id']),
                    username=row['username'],
                    email=row['email'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    is_superuser=row['is_superuser'] == '1',
                    is_staff=row['is_staff'] == '1',
                    is_active=row['is_active'] == '1'
                )
                user.set_password(row['password'])  # Set password
                user.save()
                user_map[row['id']] = user

        # Import USER_PROFILE
        self.stdout.write('Importing USER_PROFILE...')
        for row in sections.get('USER_PROFILE', []):
            if row['userprofile_id']:
                user = user_map.get(row['userprofile_id'])
                if user:
                    USER_PROFILE.objects.create(
                        userprofile=user,
                        dob=datetime.strptime(row['dob'], '%Y-%m-%d').date() if row['dob'] else None,
                        sex=row['sex'],
                        description=row['description'],
                        image=row['image']
                    )

        # Import TEST
        self.stdout.write('Importing TEST...')
        test_map = {}
        for row in sections.get('TEST', []):
            if row['test_id']:
                test = TEST.objects.create(
                    test_id=int(row['test_id']),
                    test_name=row['test_name'],
                    test_description=row['test_description'],
                    duration=datetime.strptime(row['duration'], '%H:%M:%S').time() if row['duration'] else '00:50:00'
                )
                test_map[row['test_id']] = test

        # Import QUESTION_MEDIA
        self.stdout.write('Importing QUESTION_MEDIA...')
        question_media_map = {}
        for row in sections.get('QUESTION_MEDIA', []):
            if row['questionmedia_id']:
                question_media = QUESTION_MEDIA.objects.create(
                    questionmedia_id=int(row['questionmedia_id']),
                    audio_file=row['audio_file'],
                    paragraph=row['paragraph']
                )
                question_media_map[row['questionmedia_id']] = question_media

        # Import QUESTION
        self.stdout.write('Importing QUESTION...')
        for row in sections.get('QUESTION', []):
            if row['question_id']:
                test = test_map.get(row['test'])
                question_media = question_media_map.get(row['question_media'])
                if test and question_media:
                    QUESTION.objects.create(
                        question_id=int(row['question_id']),
                        question_text=row['question_text'],
                        answer=row['answer'],
                        correct_answer=row['correct_answer'],
                        test=test,
                        questionmedia=question_media
                    )

        # Import RESULT
        self.stdout.write('Importing RESULT...')
        for row in sections.get('RESULT', []):
            if row['result_id']:
                test = test_map.get(row['test_id'])
                user = user_map.get(row['acc_id'])
                if test and user:
                    RESULT.objects.create(
                        result_id=int(row['result_id']),
                        score=int(row['score']),
                        total_questions=int(row['total_questions']),
                        test_id=test,
                        acc_id=user,
                        create_at=datetime.strptime(row['create_at'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
                    )

        # Import DOCUMENT
        self.stdout.write('Importing DOCUMENT...')
        for row in sections.get('DOCUMENT', []):
            if row['doc_id']:
                DOCUMENT.objects.create(
                    doc_id=int(row['doc_id']),
                    doc_name=row['doc_name'],
                    doc_file=row['doc_file']  # Store URL as CharField
                )

        # Import COURSE
        self.stdout.write('Importing COURSE...')
        course_map = {}
        for row in sections.get('COURSE', []):
            if row['course_id']:
                # Convert price to integer (remove VNĐ and format)
                price = int(row['price'].replace(' VNĐ', '').replace('.', '')) if row['price'] else None
                course = COURSE.objects.create(
                    course_id=int(row['course_id']),
                    course_name=row['course_name'],
                    description=row['description'],
                    price=price,
                    des_teacher=row['des_teacher'],
                    teacher_name=row['teacher_name'],
                    image=row['image']
                )
                course_map[row['course_id']] = course

        # Import PAYMENT
        self.stdout.write('Importing PAYMENT...')
        payment_map = {}
        for row in sections.get('PAYMENT', []):
            if row['payment_id']:
                course = course_map.get(row['course_id'])
                if course:
                    payment = PAYMENT.objects.create(
                        payment_id=int(row['payment_id']),
                        qr=row['QR'],
                        course_id=course,
                        account_owner=row['account_owner'],
                        account_number=row['account_number'],
                        bank_name=row['bank_name']
                    )
                    payment_map[row['payment_id']] = payment

        # Import PAYMENT_INFO
        self.stdout.write('Importing PAYMENT_INFO...')
        for row in sections.get('PAYMENT_INFO', []):
            if row['paymentinfo_id']:
                payment = payment_map.get(row['payment_id'])
                user = user_map.get(row['id'])
                if payment and user:
                    PAYMENT_INFO.objects.create(
                        paymentinfo_id=int(row['paymentinfo_id']),
                        time_at=datetime.strptime(row['time_at'], '%m/%d/%Y').replace(tzinfo=pytz.UTC),
                        payment_id=payment,
                        user=user,
                        message=row['content']
                    )

        # Import CLASS
        self.stdout.write('Importing CLASS...')
        class_map = {}
        for row in sections.get('CLASS', []):
            if row['class_id']:
                course = course_map.get(row['course'])
                if course:
                    class_obj = CLASS.objects.create(
                        class_id=int(row['class_id']),
                        class_name=row['class_name'],
                        course=course,
                        begin_time=datetime.strptime(row['begin_time'], '%m/%d/%Y').date(),
                        end_time=datetime.strptime(row['end_time'], '%m/%d/%Y').date(),
                        status=row['status']
                    )
                    class_map[row['class_id']] = class_obj

        # Import USER_CLASS
        self.stdout.write('Importing USER_CLASS...')
        user_class_map = {}
        for row in sections.get('USER_CLASS', []):
            if row['userclass_id']:
                user = user_map.get(row['user'])
                class_obj = class_map.get(row['classes'])
                if user and class_obj:
                    user_class = USER_CLASS.objects.create(
                        userclass_id=int(row['userclass_id']),
                        user=user,
                        classes=class_obj
                    )
                    user_class_map[row['userclass_id']] = user_class

        # Import LESSON
        self.stdout.write('Importing LESSON...')
        lesson_map = {}
        for row in sections.get('LESSON', []):
            if row['lesson_id']:
                course = course_map.get(row['course'])
                if course:
                    lesson = LESSON.objects.create(
                        lesson_id=int(row['lesson_id']),
                        lesson_file=row['lesson_file'],
                        exercise_file=row['excercise_file'],  # Note: CSV uses 'excercise_file'
                        course=course
                    )
                    lesson_map[row['lesson_id']] = lesson

        # Import LESSON_DETAIL
        self.stdout.write('Importing LESSON_DETAIL...')
        lesson_detail_map = {}
        for row in sections.get('LESSON_DETAIL', []):
            if row['lessondetail_id']:
                lesson = lesson_map.get(row['lesson'])
                class_obj = class_map.get(row['classes'])
                if lesson and class_obj:
                    lesson_detail = LESSON_DETAIL.objects.create(
                        lessondetail_id=int(row['lessondetail_id']),
                        lesson_name=row['lesson_name'],
                        description=row['description'],
                        lesson=lesson,
                        classes=class_obj,
                        session_number=row['session_number']
                    )
                    lesson_detail_map[row['lessondetail_id']] = lesson_detail

        # Import EXERCISE
        self.stdout.write('Importing EXERCISE...')
        exercise_map = {}
        for row in sections.get('EXCERCISE', []):  # Note: CSV uses 'EXCERCISE'
            if row['exercise_id']:
                lesson_detail = lesson_detail_map.get(row['lessondetail_id'])
                if lesson_detail:
                    exercise = EXERCISE.objects.create(
                        exercise_id=int(row['exercise_id']),
                        lessondetail=lesson_detail,
                        duedate=datetime.strptime(row['duedate'], '%m/%d/%Y').date()
                    )
                    exercise_map[row['exercise_id']] = exercise

        # Import SUBMISSION
        self.stdout.write('Importing SUBMISSION...')
        for row in sections.get('SUBMISTION', []):  # Note: CSV uses 'SUBMISTION'
            if row['submistion_id']:
                user_class = user_class_map.get(row['userclass'])
                exercise = exercise_map.get(row['excercise'])
                if user_class and exercise:
                    SUBMISSION.objects.create(
                        submission_id=int(row['submistion_id']),
                        userclass=user_class,
                        status=row['status'].lower(),
                        submit_date=datetime.strptime(row['submit_date'], '%m/%d/%Y').replace(tzinfo=pytz.UTC),
                        review=row['review'],
                        exercise=exercise
                    )

        # Import ROLLCALL
        self.stdout.write('Importing ROLLCALL...')
        rollcall_map = {}
        for row in sections.get('ROLL_CALL', []):
            if row['rollcall_id']:
                lesson_detail = lesson_detail_map.get(row['lessondetail'])
                if lesson_detail:
                    rollcall = ROLLCALL.objects.create(
                        rollcall_id=int(row['rollcall_id']),
                        lessondetail=lesson_detail
                    )
                    rollcall_map[row['rollcall_id']] = rollcall

        # Import ROLLCALL_USER
        self.stdout.write('Importing ROLLCALL_USER...')
        for row in sections.get('ROLLCALL_USER', []):
            rollcall = rollcall_map.get(row['rollcall'])
            user_class = user_class_map.get(row['userclass'])
            if rollcall and user_class:
                ROLLCALL_USER.objects.create(
                    rollcall=rollcall,
                    userclass=user_class,
                    status=row['statusrollcall'].lower()
                )

        self.stdout.write(self.style.SUCCESS('Data imported successfully!'))
