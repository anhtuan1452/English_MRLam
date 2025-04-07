from django.db import models

class KhoaHoc(models.Model):
    TenKhoaHoc_CHOICES = [
        ('English - Level 1', 'English - Level 1'),
        ('English - Level 2', 'English - Level 2'),
        ('English - Level 3', 'English - Level 3'),
    ]

    ten_khoa_hoc = models.CharField(max_length=100, choices=TenKhoaHoc_CHOICES, default='English - Level 1')

    def __str__(self):
        return self.ten_khoa_hoc

    class Meta:
        verbose_name = "Khóa học"
        verbose_name_plural = "Khóa học"


class LopHoc(models.Model):
    TRANG_THAI_CHOICES = [
        ('Đang học', 'Đang học'),
        ('Đã kết thúc', 'Đã kết thúc'),
        ('Chưa bắt đầu', 'Chưa bắt đầu')
    ]

    ten_lop = models.CharField(max_length=50)
    so_luong_hoc_vien = models.IntegerField(default=0)
    khoa_hoc = models.ForeignKey(KhoaHoc, on_delete=models.CASCADE, related_name='lop_hoc')
    ngay_bat_dau = models.DateTimeField()
    ngay_ket_thuc = models.DateTimeField()
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='Đang học')

    def __str__(self):
        return self.ten_lop

    class Meta:
        verbose_name = "Lớp học"
        verbose_name_plural = "Lớp học"
