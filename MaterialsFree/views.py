from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from english.models import DOCUMENT  # Đảm bảo bạn import đúng từ models
from .forms import DocumentSearchForm  # Form tìm kiếm tài liệu

def materials_list(request):
    """Hiển thị danh sách tài liệu miễn phí (documents)"""

    documents = DOCUMENT.objects.all()  # Lấy tất cả tài liệu
    search_form = DocumentSearchForm(request.GET)  # Form tìm kiếm từ GET

    # Kiểm tra nếu form tìm kiếm hợp lệ và có giá trị tìm kiếm
    if search_form.is_valid() and search_form.cleaned_data['search']:
        query = search_form.cleaned_data['search']  # Lấy giá trị tìm kiếm
        # Lọc tài liệu theo tên tài liệu
        documents = documents.filter(doc_name__icontains=query)

    context = {
        'search_form': search_form,  # Gửi form tìm kiếm vào context
        'documents': documents,  # Gửi danh sách tất cả tài liệu vào context
        'active_menu': 'materials',  # Menu đang hoạt động
        'title': 'Tài liệu miễn phí'  # Tiêu đề trang
    }
    return render(request, 'materials_list.html', context)  # Render template materials_list.html

def materials_detail(request, doc_id):
    """Chi tiết tài liệu"""

    document = get_object_or_404(DOCUMENT, doc_id=doc_id)  # Lấy tài liệu theo doc_id hoặc trả về lỗi 404 nếu không tìm thấy

    context = {
        'document': document,  # Gửi tài liệu vào context
        'active_menu': 'materials',  # Menu đang hoạt động
        'title': document.doc_name  # Tiêu đề trang là tên tài liệu
    }
    return render(request, 'materials_detail.html', context)  # Render template materials_detail.html