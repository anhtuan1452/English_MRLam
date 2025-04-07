from django.contrib import admin
from .models import KhoaHoc, TaiLieu

@admin.register(KhoaHoc)
class KhoaHocAdmin(admin.ModelAdmin):
    list_display = ('ten_khoa_hoc',)
    search_fields = ('ten_khoa_hoc',)

@admin.register(TaiLieu)
class TaiLieuAdmin(admin.ModelAdmin):
    list_display = ('ma_tai_lieu', 'ten_tai_lieu', 'khoa_hoc', 'file_type', 'ngay_tao')
    list_filter = ('khoa_hoc', 'file_type')
    search_fields = ('ma_tai_lieu', 'ten_tai_lieu', 'mo_ta')
    date_hierarchy = 'ngay_tao'

