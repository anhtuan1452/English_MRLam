import datetime

from django.db import models


class TEST(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=100)
    test_description = models.CharField(max_length=255, null=True, blank=True)  # Adding this field if needed
    duration = models.TimeField()
    class Meta:
        db_table = 'TEST'

class QUESTION(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    answer = models.TextField(null=True, blank=True)
    correct_answer = models.CharField(max_length=50, null=True, blank=True)
    test = models.ForeignKey(TEST, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Question'


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class ACCOUNT(AbstractBaseUser):
    acc_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100,default='tuan')
    last_name = models.CharField(max_length=100,default='anh')
    date_joined = models.DateTimeField(default=datetime.datetime.now)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    # REQUIRED_FIELDS sẽ là các trường bạn muốn yêu cầu khi tạo superuser
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    USERNAME_FIELD = 'username'

    # `USERNAME_FIELD` mặc định là 'username', các trường yêu cầu khác là 'email' và 'first_name'

    def __str__(self):
        return self.username
    class Meta:
        db_table = 'ACCOUNT'



class RESULT(models.Model):
    result_id = models.AutoField(primary_key=True)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    test_id = models.ForeignKey(TEST, on_delete=models.CASCADE)
    acc_id = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)
    correct_answers = models.IntegerField()
    incorrect_answers = models.IntegerField()
    create_at = models.DateTimeField(default=datetime.datetime.now)
    class Meta:
        db_table = 'RESULT'


class DOCUMENT(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=100)
    doc_file = models.FileField(upload_to='documents/', null=True, blank=True)

    class Meta:
        db_table = 'DOCUMENT'


class COURSE(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    des_teacher = models.CharField(max_length=100, null=True, blank=True)
    teacher_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.CharField(max_length=100,null=True, blank=True)
    class Meta:
        db_table = 'COURSE'


class PAYMENT(models.Model):
    payment_id = models.AutoField(primary_key=True)
    qr = models.CharField(max_length=100,null=True, blank=True)
    course_id = models.ForeignKey(COURSE, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=100,null = True)
    account_number = models.CharField(max_length=100,null = True)
    class Meta:
        db_table = 'PAYMENT'

class PAYMENT_INFO(models.Model):
    paymentinfo_id = models.AutoField(primary_key=True)
    time_at = models.DateTimeField(default=datetime.datetime.now())
    payment_id = models.ForeignKey(PAYMENT, on_delete=models.CASCADE)
    acc_id = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)

class CLASS(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=50)
    course = models.ForeignKey(COURSE, on_delete=models.CASCADE)
    begin_time = models.DateField()
    end_time = models.DateField()

    class Meta:
        db_table = 'CLASS'


class USER_CLASS(models.Model):
    userclass_id = models.AutoField(primary_key=True)
    acc_id = models.ForeignKey(ACCOUNT, on_delete=models.CASCADE)
    class_id = models.ForeignKey(CLASS, on_delete=models.CASCADE)

    class Meta:
        db_table = 'USER_CLASS'


class LESSON(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    lesson_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    lesson_file = models.FileField()
    exercise_file = models.FileField()
    course = models.ForeignKey(COURSE, on_delete=models.CASCADE)

    class Meta:
        db_table = 'LESSON'


class LESSON_DETAIL(models.Model):
    lessondetail_id = models.AutoField(primary_key=True)
    lesson_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    lesson_id = models.ForeignKey(LESSON, on_delete=models.CASCADE)
    class_instance = models.ForeignKey(CLASS, on_delete=models.CASCADE)
    session_number = models.CharField(null=True)
    class Meta:
        db_table = 'LessonDetail'


class EXERCISE(models.Model):
    exercise_id = models.AutoField(primary_key=True)
    lessondetail_id = models.ForeignKey(LESSON_DETAIL, on_delete=models.CASCADE)
    duedate = models.DateField()
    class Meta:
        db_table = 'EXERCISE'

class SUBMISSION(models.Model):
    STATUS_CHOICES = (
        ('done', 'Done'),
        ('check', 'Check'),
    )

    submission_id = models.AutoField(primary_key=True)
    userclass_id = models.ForeignKey(USER_CLASS, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    submit_date = models.DateTimeField(default=datetime.datetime.now())
    review = models.TextField(null=True, blank=True)
    exercise_id = models.ForeignKey(EXERCISE, on_delete=models.CASCADE)

    class Meta:
        db_table = 'SUBMISSION'


class ROLLCALL(models.Model):
    rollcall_id = models.AutoField(primary_key=True)
    lessondetail_id = models.ForeignKey(LESSON_DETAIL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ROLL_CALL'


class ROLLCALL_USER(models.Model):
    rollcall = models.ForeignKey(ROLLCALL, on_delete=models.CASCADE)
    userclass = models.ForeignKey(USER_CLASS, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    statusrollcall = models.CharField(max_length=100,choices=STATUS_CHOICES)
    class Meta:
        db_table = 'ROLL_CALL_USER'