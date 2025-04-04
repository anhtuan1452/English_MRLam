from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class AccountManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class Account(AbstractBaseUser, PermissionsMixin):
    # acc_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Django will hash this
    role = models.CharField(max_length=20, choices=[
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator')
    ])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username


class User(models.Model):
    # user_id = models.AutoField(primary_key=True)
    acc = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='user_profile')
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], null=True, blank=True)
    image = models.ImageField(upload_to='user_images/', null=True, blank=True)

    # def __str__(self):
    #     return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    """Khóa học"""
    # course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    route = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=200)
    des_teacher = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True)

    # def __str__(self):
    #     return self.course_name


class Class(models.Model):
    """Lớp học"""
    # class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='classes')
    description = models.TextField(null=True, blank=True)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    # def __str__(self):
    #     return self.class_name


class UserClass(models.Model):
    # userclass_id = models.AutoField(primary_key=True)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='enrollments')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_classes')

    # class Meta:
    #     unique_together = ('class_ref', 'user')
    #
    # def __str__(self):
    #     return f"{self.user} enrolled in {self.class_ref}"


class LessonDetail(models.Model):
    """Buổi chi tiết"""
    # id_lessondetail = models.AutoField(primary_key=True)
    lesson_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
# thieus fk
    # def __str__(self):
    #     return self.lesson_name


class Lesson(models.Model):
    """Buổi học"""
    # lesson_id = models.AutoField(primary_key=True)
    lesson_name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    lesson_file = models.FileField(upload_to='lesson_files/', null=True, blank=True)
    exercise_file = models.FileField(upload_to='exercise_files/', null=True, blank=True)
    lessondetail_id = models.ForeignKey(LessonDetail, on_delete=models.CASCADE, related_name='lessons', null=True,
                                        blank=True)
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')

    # def __str__(self):
    #     return self.lesson_name


class Exercise(models.Model):
    """Bài tập"""
    # exercise_id = models.AutoField(primary_key=True)
    lessondetail_id = models.ForeignKey(LessonDetail, on_delete=models.CASCADE, related_name='exercises')
    submission = models.FileField(upload_to='submission_files/', null=True, blank=True)
    review = models.TextField(null=True, blank=True)

    # def __str__(self):
    #     return f"Exercise for {self.id_lessondetail}"


class Payment(models.Model):
    # id = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='payments')
    QR = models.CharField(max_length=255, null=True, blank=True)
    # payment_date = models.DateTimeField(auto_now_add=True)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    # status = models.CharField(max_length=20, choices=[
    #     ('pending', 'Pending'),
    #     ('completed', 'Completed'),
    #     ('failed', 'Failed')
    # ], default='pending')

    # def __str__(self):
    #     return f"Payment {self.id} for {self.course}"


class Test(models.Model):
    # test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=200)
    test_des = models.TextField(null=True, blank=True)

    # def __str__(self):
    #     return self.test_name


class Question(models.Model):
    # question_id = models.AutoField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    answer = models.TextField(null=True, blank=True)
    correct_answer = models.TextField()

    # def __str__(self):
    #     return f"Question for {self.test}"


class Result(models.Model):
    # result_id = models.AutoField(primary_key=True)
    test_id = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='results')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='test_results')
    results = models.TextField()  # Could be JSON or serialized data

    # def __str__(self):
    #     return f"Result for {self.test} by {self.user}"


class Document(models.Model):
    # doc_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    doc_name = models.CharField(max_length=200)
    doc_file = models.FileField(upload_to='documents/')

    # def __str__(self):
    #     return self.doc_name


class RollCall(models.Model):
    """Điểm danh"""
    # rollcall_id = models.AutoField(primary_key=True)
    lessondetail_id = models.ForeignKey(LessonDetail, on_delete=models.CASCADE, related_name='roll_calls')
    state = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
    ])
    student_name = models.CharField(max_length=200)

    # def __str__(self):
    #     return f"Roll call for {self.student_name} in {self.id_lessondetail}"


class CatchUpLesson(models.Model):
    """Học bù"""
    # catch_up_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='catch_up_lessons')
    lessondetail_id = models.ForeignKey(LessonDetail, on_delete=models.CASCADE, related_name='catch_ups')

    # def __str__(self):
    #     return f"Catch-up lesson for {self.user} on {self.id_lessondetail}"