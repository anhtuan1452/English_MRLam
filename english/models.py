from django.db import models


class Test(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=100)
    test_description = models.CharField(max_length=255, null=True, blank=True)  # Adding this field if needed
    time = models.TimeField()

    class Meta:
        db_table = 'TEST'

class Question(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    answer = models.TextField(null=True, blank=True)
    correct_answer = models.CharField(max_length=50, null=True, blank=True)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Question'


class Account(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    acc_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    class Meta:
        db_table = 'ACCOUNT'


class UserProfile(models.Model):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateField()
    sex = models.CharField(max_length=10)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    class Meta:
        db_table = 'USER_PROFILE'


class Result(models.Model):
    result_id = models.AutoField(primary_key=True)
    result = models.IntegerField()
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    class Meta:
        db_table = 'RESULT'


class Document(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=100)
    doc_file = models.FileField(upload_to='documents/', null=True, blank=True)

    class Meta:
        db_table = 'DOCUMENT'


class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    des_teacher = models.CharField(max_length=100, null=True, blank=True)
    teacher_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.BinaryField(null=True, blank=True)

    class Meta:
        db_table = 'COURSE'


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    qr = models.BinaryField(null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PAYMENT'


class Class(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=50)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    begin_time = models.DateField()
    end_time = models.DateField()

    class Meta:
        db_table = 'CLASS'


class UserClass(models.Model):
    userclass_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)

    class Meta:
        db_table = 'USER_CLASS'


class Lesson(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    lesson_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    lesson_file = models.CharField(max_length=255, null=True, blank=True)
    exercise_file = models.CharField(max_length=255, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        db_table = 'LESSON'


class LessonDetail(models.Model):
    lessonDetail_id = models.AutoField(primary_key=True)
    lesson_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE)

    class Meta:
        db_table = 'LessonDetail'


class Exercise(models.Model):
    exercise_id = models.AutoField(primary_key=True)
    lesson_detail = models.ForeignKey(LessonDetail, on_delete=models.CASCADE)
    duedate = models.DateField()

    class Meta:
        db_table = 'EXERCISE'


class Submission(models.Model):
    STATUS_CHOICES = (
        ('done', 'Done'),
        ('check', 'Check'),
    )

    submission_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    submit_date = models.DateField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    class Meta:
        db_table = 'SUBMISSION'


class RollCall(models.Model):
    rollcall_id = models.AutoField(primary_key=True)
    lesson_detail = models.ForeignKey(LessonDetail, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ROLL_CALL'


class RollCallUser(models.Model):
    rollcall = models.ForeignKey(RollCall, on_delete=models.CASCADE)
    userclass = models.ForeignKey(UserClass, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ROLL_CALL_USER'