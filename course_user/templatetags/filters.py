# from django import template
# import re
#
# register = template.Library()
#
#
# @register.filter
# def format_text(value):
#     if not value:
#         return ''
#
#     # Loại bỏ dấu xuống dòng lạ giữa các từ (tránh bị ngắt giữa từ)
#     value = re.sub(r'([a-zA-ZÀ-ỹ])\n([a-zA-ZÀ-ỹ])', r'\1 \2', value)
#
#     # Chuẩn hóa xuống dòng
#     value = re.sub(r'\n+', ' ', value)
#
#     # Giữ lại in đậm cho các tiêu đề phần
#     section_titles = [
#         "Nội dung khóa học:",
#         "Kết quả sau khóa học:",
#         "Cam kết đầu ra:",
#         "Mục tiêu khóa học:",
#     ]
#     for title in section_titles:
#         value = value.replace(title, f'<br><br><strong>{title}</strong><br>')
#
#     # Ngắt dòng sau dấu cộng
#     value = re.sub(r'\+\s*', r'<br>+ ', value)
#
#     # Xử lý tên và chức danh - không in đậm
#     if re.search(r'[A-ZÀ-Ỹ][a-zà-ỹ]+ [A-ZÀ-Ỹ][a-zà-ỹ]+ [A-ZÀ-Ỹ][a-zà-ỹ]+\s+Giảng viên', value):
#         value = re.sub(r'(Giảng viên)', r'<br>\1<br>', value)
#
#     # Xử lý các chứng chỉ ngôn ngữ (TOEIC, IELTS) - không in đậm
#     value = re.sub(r'(TOEIC \d{3}/\d{3})', r'<br>\1<br>', value)
#     value = re.sub(r'(IELTS \d+\.\d+)', r'<br>\1<br>', value)
#
#     # Xử lý bằng cấp và trường học - không in đậm
#     value = re.sub(r'(Cử nhân [^–]+)–([^I^T^0-9]+)', r'<br>\1 – \2<br>', value)
#
#     # Xử lý chứng chỉ TESOL - không in đậm
#     value = re.sub(r'(Chứng chỉ TESOL[^I^T^0-9]*)', r'<br>\1<br>', value)
#
#     # Xử lý kinh nghiệm - nhiều mẫu khác nhau - không in đậm
#     exp_patterns = [
#         r'(Có nhiều năm kinh nghiệm[^\.]*\.?)',
#         r'(\d+ năm kinh nghiệm[^\.]*\.?)',
#     ]
#     for pattern in exp_patterns:
#         value = re.sub(pattern, r'<br>\1<br>', value)
#
#     # Xử lý phong cách dạy học - nhiều mẫu khác nhau - không in đậm
#     style_patterns = [
#         r'(Phong cách dạy học[^\.]*\.?)',
#         r'(Phong cách giảng dạy[^\.]*\.?)',
#     ]
#     for pattern in style_patterns:
#         value = re.sub(pattern, r'<br>\1<br>', value)
#
#     # Xử lý đặc biệt cho "TP. Hồ Chí Minh" để tránh ngắt dòng sau "TP."
#     value = re.sub(r'TP\.\s+Hồ Chí Minh', r'TP. Hồ Chí Minh', value)
#
#     # Chuẩn hóa dấu chấm + viết hoa sau dấu chấm (áp dụng sau khi đã xử lý các trường hợp đặc biệt)
#     value = re.sub(r'\.(\s*)(?=[A-ZÀ-Ỹ])', r'.<br>', value)
#
#     # Loại bỏ các khoảng trắng dư hoặc dòng trống
#     value = re.sub(r'(<br>\s*)+', r'<br>', value)
#     value = re.sub(r'^<br>', '', value)  # Loại bỏ <br> ở đầu văn bản
#
#     return value.strip()
from django import template
import re

register = template.Library()


@register.filter
def format_text(value):
    if not value:
        return ''

    # --- Loại bỏ xuống dòng giữa từ ---
    value = re.sub(r'([a-zA-ZÀ-ỹ])\n([a-zA-ZÀ-ỹ])', r'\1 \2', value)

    # --- Chuẩn hóa xuống dòng thành khoảng trắng ---
    value = re.sub(r'\n+', ' ', value)

    # --- Xử lý tiêu đề cho mô tả khóa học ---
    section_titles = [
        "Nội dung khóa học:",
        "Kết quả sau khóa học:",
        "Cam kết đầu ra:",
        "Mục tiêu khóa học:",
        "Lộ trình học:",
        "Thời lượng khóa học:",
        "Đối tượng học viên:",
    ]
    for title in section_titles:
        value = value.replace(title, f'<br><br><strong>{title}</strong><br>')

    # --- Ngắt dòng sau dấu cộng ---
    value = re.sub(r'\+\s*', r'<br>+ ', value)

    # --- Xử lý thông tin giáo viên ---
    # Xử lý tên giáo viên
    value = re.sub(r'(Ms|Mr)\s+([A-ZÀ-Ỹ][a-zà-ỹ]+)', r'<br><strong>\1 \2</strong><br>', value)

    # Xử lý chức danh "Giảng viên"
    value = re.sub(r'(Giảng viên)', r'\1<br>', value)

    # Xử lý bằng cấp và trường học
    value = re.sub(
        r'(Cử nhân [^–]+)–([^I^T^0-9]+)',
        r'\1 – \2<br>',
        value
    )

    # Xử lý các chứng chỉ ngôn ngữ (TOEIC, IELTS)
    value = re.sub(r'(TOEIC \d{3}(/\d{3})?)', r'\1<br>', value)
    value = re.sub(r'(IELTS \d+(\.\d+)?)', r'\1<br>', value)

    # Xử lý chứng chỉ TESOL
    value = re.sub(r'(Chứng chỉ TESOL[^<]*)', r'\1<br>', value)

    # Xử lý kinh nghiệm
    value = re.sub(r'(\d+ năm kinh nghiệm[^<]*)', r'\1<br>', value)
    value = re.sub(r'(Có nhiều năm kinh nghiệm[^<]*)', r'\1<br>', value)

    # Xử lý phong cách dạy học - FIX HERE
    value = re.sub(r'(Phong cách giảng dạy[^<]*)', r'\1<br>', value)
    # Thêm pattern riêng cho "Phong cách" không có từ "giảng"
    value = re.sub(r'(Phong cách dạy[^<]*)', r'\1<br>', value)

    # Tránh ngắt "TP. Hồ Chí Minh"
    value = re.sub(r'TP\.\s+Hồ Chí Minh', r'TP. Hồ Chí Minh', value)

    # Ngắt dòng sau dấu chấm (trừ "TP.")
    value = re.sub(r'(?<!TP)\.(\s*)(?=[A-ZÀ-Ỹ])', r'.<br>', value)

    # Loại bỏ khoảng trắng/dòng thừa do nhiều <br> liền nhau
    value = re.sub(r'(<br>\s*)+', r'<br>', value)
    value = re.sub(r'^<br>', '', value)

    return value.strip()