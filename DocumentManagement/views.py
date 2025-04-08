from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from .models import TaiLieu, KhoaHoc
from .forms import TaiLieuForm


def document_list(request):
    """Hiển thị danh sách tài liệu"""
    search_term = request.GET.get('search', '')

    if search_term:
        documents = TaiLieu.objects.filter(
            Q(ma_tai_lieu__icontains=search_term) |
            Q(ten_tai_lieu__icontains=search_term) |
            Q(khoa_hoc__ten_khoa_hoc__icontains=search_term)
        ).order_by('-ngay_tao')  # Sắp xếp theo ngày tạo mới nhất
    else:
        documents = TaiLieu.objects.all().order_by('-ngay_tao')  # Sắp xếp theo ngày tạo mới nhất

    # In ra số lượng tài liệu để debug
    print(f"Số lượng tài liệu: {documents.count()}")

    context = {
        'title': 'Danh sách tài liệu',
        'danh_sach_tai_lieu': documents,
        'search_term': search_term
    }

    return render(request, 'ql_tailieu.html', context)


def document_detail(request, document_id):
    """Hiển thị chi tiết tài liệu"""
    document = get_object_or_404(TaiLieu, id=document_id)

    context = {
        'title': 'Chi tiết tài liệu',
        'document': document
    }

    return render(request, 'document_detail.html', context)


def add_document(request):
    """Thêm tài liệu mới"""
    khoa_hoc_list = KhoaHoc.objects.all()

    if request.method == 'POST':
        form = TaiLieuForm(request.POST, request.FILES)
        if form.is_valid():
            # Nếu có trường noi_dung, lưu vào mo_ta
            noi_dung = request.POST.get('noi_dung', '')
            if noi_dung:
                form.instance.mo_ta = f"{form.instance.mo_ta}\n\n{noi_dung}" if form.instance.mo_ta else noi_dung

            # Tự động xác định loại file nếu không được chọn
            if not form.instance.file_type and form.instance.file_tai_lieu:
                file_name = form.instance.file_tai_lieu.name
                extension = file_name.split('.')[-1].upper()
                if extension in ['PDF', 'DOC', 'DOCX', 'XLS', 'XLSX', 'PPT', 'PPTX', 'ZIP', 'RAR']:
                    form.instance.file_type = extension
                else:
                    form.instance.file_type = 'OTHER'

            # Lưu tài liệu
            tai_lieu = form.save()

            # In thông tin tài liệu để debug
            print(f"Đã lưu tài liệu: ID={tai_lieu.id}, Tên={tai_lieu.ten_tai_lieu}")

            messages.success(request, 'Thêm tài liệu thành công!')

            # Chuyển hướng đến trang danh sách tài liệu
            return redirect('DocumentManagement:document_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
            print(f"Lỗi form: {form.errors}")  # In lỗi để debug

    context = {
        'title': 'Thêm tài liệu',
        'khoa_hoc_list': khoa_hoc_list
    }

    return render(request, 'add_document.html', context)


def edit_document(request, document_id):
    """Sửa thông tin tài liệu"""
    document = get_object_or_404(TaiLieu, id=document_id)
    khoa_hoc_list = KhoaHoc.objects.all()

    if request.method == 'POST':
        form = TaiLieuForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            # Nếu có trường noi_dung, lưu vào mo_ta
            noi_dung = request.POST.get('noi_dung', '')
            if noi_dung:
                form.instance.mo_ta = f"{form.instance.mo_ta}\n\n{noi_dung}" if form.instance.mo_ta else noi_dung

            # Nếu không có file mới được tải lên, giữ nguyên file cũ
            if not request.FILES.get('file_tai_lieu'):
                form.instance.file_tai_lieu = document.file_tai_lieu
            else:
                # Tự động xác định loại file nếu có file mới
                file_name = request.FILES.get('file_tai_lieu').name
                extension = file_name.split('.')[-1].upper()
                if extension in ['PDF', 'DOC', 'DOCX', 'XLS', 'XLSX', 'PPT', 'PPTX', 'ZIP', 'RAR']:
                    form.instance.file_type = extension

            form.save()
            messages.success(request, 'Cập nhật tài liệu thành công!')

            # Chuyển hướng đến trang danh sách tài liệu
            return redirect('DocumentManagement:document_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
            print(form.errors)  # In lỗi để debug

    context = {
        'title': 'Sửa tài liệu',
        'document': document,
        'khoa_hoc_list': khoa_hoc_list
    }

    return render(request, 'edit_document.html', context)


def delete_document(request, document_id):
    """Xóa tài liệu"""
    document = get_object_or_404(TaiLieu, id=document_id)

    if request.method == 'POST':
        document.delete()
        messages.success(request, 'Xóa tài liệu thành công!')

        # Chuyển hướng đến trang danh sách tài liệu
        return redirect('DocumentManagement:document_list')

    context = {
        'title': 'Xóa tài liệu',
        'document': document
    }

    return render(request, 'delete_document.html', context)