from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import KhoaHoc, LopHoc

@admin.register(KhoaHoc)
class KhoaHocAdmin(admin.ModelAdmin):
    list_display = ('ten_khoa_hoc',)
    search_fields = ('ten_khoa_hoc',)

@admin.register(LopHoc)
class LopHocAdmin(admin.ModelAdmin):
    list_display = ('ten_lop', 'khoa_hoc', 'so_luong_hoc_vien', 'ngay_bat_dau', 'ngay_ket_thuc', 'trang_thai')
    list_filter = ('trang_thai', 'khoa_hoc')
    search_fields = ('ten_lop', 'khoa_hoc__ten_khoa_hoc')
