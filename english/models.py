import datetime

from django.contrib.auth.models import User
from django.db import models


class USER_PROFILE(models.Model):
    userprofile = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    dob = models.DateField(default="")  # ngày sinh
    sex = models.CharField(max_length=1, choices=SEX_CHOICES,null=True)  # giới tính (có choices)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='media/avatars', null=True, blank=True)
    reset_password_token = models.CharField(max_length=100,default="")
    reset_password_expiry = models.CharField(max_length=100,default="")
    def __str__(self):
        return self.user.username

    class Meta:
        db_table = 'USER_PROFILE'

class TEST(models.Model):
    test_id = models.AutoField(primary_key=True)
    test_name = models.CharField(max_length=255)
    test_description = models.TextField(null=True, blank=True)  # Adding this field if needed
    duration = models.PositiveIntegerField(default=30)
    class Meta:
        db_table = 'TEST'


class QUESTION_MEDIA(models.Model):
    questionmedia_id = models.AutoField(primary_key=True)
    audio_file = models.FileField(upload_to='media/audio', null=True, blank=True)
    paragraph = models.TextField(null=True, blank=True)
    # def __str__(self):
    #     parts = []
    #     if self.audio_file:
    #         parts.append("🎧 Audio")
    #     if self.paragraph:
    #         parts.append("📖 Paragraph")
    #     return " + ".join(parts) or "❓ Chưa có nội dung"
    class Meta:
        db_table = 'QUESTION_MEDIA'


class QUESTION(models.Model):
    question_id = models.AutoField(primary_key=True)
    question_text = models.TextField()
    answer = models.JSONField(null=True, blank=True)
    correct_answer = models.CharField(max_length=50, null=True, blank=True)
    test = models.ForeignKey(TEST, on_delete=models.CASCADE)
    question_media = models.ForeignKey(QUESTION_MEDIA, on_delete=models.SET_NULL, null=True, blank=True)
    class Meta:
        db_table = 'QUESTION'


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager




class RESULT(models.Model):
    result_id = models.AutoField(primary_key=True)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    test = models.ForeignKey(TEST, on_delete=models.CASCADE)
    acc = models.ForeignKey(User, on_delete=models.CASCADE)
    create_at = models.DateTimeField(default=datetime.datetime.now)
    user_answer = models.JSONField(null=True, blank=True)  # Lưu câu trả lời của người dùng
    class Meta:
        db_table = 'RESULT'

class DOCUMENT(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=100)
    doc_file = models.FileField(upload_to='media/documents', null=True, blank=True)
    auth_user_id = models.ForeignKey(User, on_delete=models.CASCADE,
        default=1,)
    class Meta:
        db_table = 'DOCUMENT'


class COURSE(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    des_teacher = models.CharField(max_length=100, null=True, blank=True)
    teacher_name = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="media/course",null=True, blank=True)
    def __str__(self):
        return self.course_name
    class Meta:
        db_table = 'COURSE'


class PAYMENT(models.Model):
    payment_id = models.AutoField(primary_key=True)
    qr = models.ImageField(upload_to='media/Qr', null=True, blank=True)
    course_id = models.ForeignKey(COURSE, on_delete=models.CASCADE)
    account_owner = models.CharField(max_length=100,null = True)
    account_number = models.CharField(max_length=100,null = True)
    bank_name = models.CharField(max_length=100)
    class Meta:
        db_table = 'PAYMENT'

class PAYMENT_INFO(models.Model):
    paymentinfo_id = models.AutoField(primary_key=True)
    time_at = models.DateTimeField(default=datetime.datetime.now())
    payment = models.ForeignKey(PAYMENT, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=150)
    class Meta:
        db_table = 'PAYMENT_INFO'

class CLASS(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Đang học'),
        ('starting', 'Đang bắt đầu'),
        ('finished', 'Đã kết thúc'),
    ]
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=50)
    course = models.ForeignKey(COURSE, on_delete=models.CASCADE)
    begin_time = models.DateField()
    end_time = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    timetable = models.CharField(max_length=1000,null=True,blank=True)
    class Meta:
        db_table = 'CLASS'


class USER_CLASS(models.Model):
    userclass_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classes = models.ForeignKey(CLASS, on_delete=models.CASCADE)

    class Meta:
        db_table = 'USER_CLASS'


# Trong models.py
class LESSON(models.Model):
    lesson_id = models.AutoField(primary_key=True)
    lesson_file = models.FileField(upload_to="media/lesson", max_length=200)  # Thay FileField bằng URLField
    exercise_file = models.FileField(upload_to="media/exercise", max_length=200)  # Thay FileField bằng URLField
    lesson_name = models.CharField(max_length=100, default="chua co")
    description = models.TextField(null=True, blank=True)
    course = models.ForeignKey(COURSE, on_delete=models.CASCADE)
    session_number = models.CharField(max_length=100, null=True)
    class Meta:
        db_table = 'LESSON'


class LESSON_DETAIL(models.Model):
    lessondetail_id = models.AutoField(primary_key=True)
    lesson = models.ForeignKey(LESSON, on_delete=models.CASCADE)
    classes = models.ForeignKey(CLASS, on_delete=models.CASCADE)
    date = models.DateField(null=True,blank=True)
    class Meta:
        db_table = 'LESSON_DETAIL'


class EXERCISE(models.Model):
    exercise_id = models.AutoField(primary_key=True)
    lessondetail = models.OneToOneField(LESSON_DETAIL, on_delete=models.CASCADE)
    duedate = models.DateField()
    class Meta:
        db_table = 'EXERCISE'


class SUBMISSION(models.Model):
    STATUS_CHOICES = (
        ('done', 'Done'),
        ('check', 'Check'),
    )

    submission_id = models.AutoField(primary_key=True)
    userclass = models.ForeignKey(USER_CLASS, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    submit_date = models.DateTimeField(default=datetime.datetime.now)
    review = models.TextField(null=True, blank=True)
    exercise = models.ForeignKey(EXERCISE, on_delete=models.CASCADE)
    submission_file_content = models.FileField(upload_to="media/file_submission",null=True, blank=True)  # Lưu nội dung nhị phân của tệp
    submission_file_name = models.CharField(max_length=255, null=True, blank=True)  # Lưu tên tệp
    submission_file_type = models.CharField(max_length=50, null=True, blank=True)  # Lưu loại tệp (e.g., .pdf, .docx)

    class Meta:
        db_table = 'SUBMISSION'


class ROLLCALL(models.Model):
    rollcall_id = models.AutoField(primary_key=True)
    lessondetail = models.OneToOneField(LESSON_DETAIL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ROLL_CALL'


class ROLLCALL_USER(models.Model):
    rollcall = models.ForeignKey(ROLLCALL, on_delete=models.CASCADE)
    userclass = models.ForeignKey(USER_CLASS, on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
    )
    status = models.CharField(max_length=100,choices=STATUS_CHOICES)
    class Meta:
        db_table = 'ROLL_CALL_USER'