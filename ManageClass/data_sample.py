import os
import django
import datetime
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'English_MRLam.settings')
django.setup()

from QLlophoc.models import KhoaHoc, LopHoc


def populate_data():
    # Create courses
    toiec_lv1 = KhoaHoc.objects.create(ten_khoa_hoc='Toiec Lv.1')
    toiec_lv2 = KhoaHoc.objects.create(ten_khoa_hoc='Toiec Lv.2')
    toiec_lv3 = KhoaHoc.objects.create(ten_khoa_hoc='Toiec Lv.3')

    # Create classes
    class_data = [
        {
            'ten_lop': 'KN223',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv1,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 12, 15, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2024, 4, 15, 9, 0)),
            'trang_thai': 'Đang học'
        },
        {
            'ten_lop': 'KN227',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv1,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 4, 15, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2023, 7, 15, 9, 0)),
            'trang_thai': 'Đã kết thúc'
        },
        {
            'ten_lop': 'ST332',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv2,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 5, 14, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2020, 5, 14, 9, 0)),
            'trang_thai': 'Đang học'
        },
        {
            'ten_lop': 'ST331',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv3,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 2, 12, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2023, 5, 12, 9, 0)),
            'trang_thai': 'Đang học'
        },
        {
            'ten_lop': 'ST330',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv2,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 1, 1, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2023, 4, 1, 9, 0)),
            'trang_thai': 'Đang học'
        },
        {
            'ten_lop': 'KN226',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv2,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 8, 29, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2024, 12, 28, 9, 0)),
            'trang_thai': 'Đã kết thúc'
        },
        {
            'ten_lop': 'KN228',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv3,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2024, 3, 30, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2024, 6, 15, 9, 0)),
            'trang_thai': 'Đã kết thúc'
        },
        {
            'ten_lop': 'KN224',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv1,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 10, 25, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2024, 2, 25, 9, 0)),
            'trang_thai': 'Đã kết thúc'
        },
        {
            'ten_lop': 'KN223',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv1,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 7, 20, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2023, 11, 20, 9, 0)),
            'trang_thai': 'Đã kết thúc'
        },
        {
            'ten_lop': 'KN222',
            'so_luong_hoc_vien': 30,
            'khoa_hoc': toiec_lv2,
            'ngay_bat_dau': timezone.make_aware(datetime.datetime(2023, 5, 15, 9, 0)),
            'ngay_ket_thuc': timezone.make_aware(datetime.datetime(2023, 8, 15, 9, 0)),
            'trang_thai': 'Đã kết thúc'
        }
    ]

    for data in class_data:
        LopHoc.objects.create(**data)

    print("Dữ liệu mẫu đã được thêm thành công!")


if __name__ == '__main__':
    print("Đang thêm dữ liệu mẫu...")
    populate_data()

