# from django.db import models
# from django.utils import timezone
#
#
# class KhoaHoc(models.Model):
#     ten_khoa_hoc = models.CharField(max_length=100)
#
#     def __str__(self):
#         return self.ten_khoa_hoc
#
#     class Meta:
#         verbose_name = "Khóa học"
#         verbose_name_plural = "Khóa học"
#
#
# class TaiLieu(models.Model):
#     ma_tai_lieu = models.CharField(max_length=20)
#     ten_tai_lieu = models.CharField(max_length=255)
#     mo_ta = models.TextField(blank=True, null=True)
#     khoa_hoc = models.ForeignKey(KhoaHoc, on_delete=models.CASCADE, related_name='tai_lieu')
#     file_type = models.CharField(max_length=10, default='PDF')
#     file_tai_lieu = models.FileField(upload_to='tai_lieu/')
#     ngay_tao = models.DateField(default=timezone.now)
#     ngay_cap_nhat = models.DateField(auto_now=True)
#
#     def __str__(self):
#         return f"{self.ma_tai_lieu} - {self.ten_tai_lieu}"
#
#     class Meta:
#         verbose_name = "Tài liệu"
#         verbose_name_plural = "Tài liệu"
#         ordering = ['-ngay_tao']
#
# Đây là một ví dụ, bạn cần giữ nguyên model của mình
from django.db import models
from django.utils import timezone


class KhoaHoc(models.Model):
    ten_khoa_hoc = models.CharField(max_length=255)
    mo_ta = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.ten_khoa_hoc


class TaiLieu(models.Model):
    FILE_TYPES = (
        ('PDF', 'PDF'),
        ('DOC', 'DOC'),
        ('DOCX', 'DOCX'),
        ('XLS', 'XLS'),
        ('XLSX', 'XLSX'),
        ('PPT', 'PPT'),
        ('PPTX', 'PPTX'),
        ('ZIP', 'ZIP'),
        ('RAR', 'RAR'),
        ('OTHER', 'Khác'),
    )

    ma_tai_lieu = models.CharField(max_length=50, unique=True)
    ten_tai_lieu = models.CharField(max_length=255)
    mo_ta = models.TextField(blank=True, null=True)
    file_tai_lieu = models.FileField(upload_to='tai_lieu/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES, default='PDF')
    khoa_hoc = models.ForeignKey(KhoaHoc, on_delete=models.CASCADE, related_name='tai_lieu')
    ngay_tao = models.DateTimeField(default=timezone.now)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ten_tai_lieu