from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import DocumentForm
from english.models import Document
import os


def document_list(request):
    documents = Document.objects.all().order_by('-doc_id')
    context = {
        'documents': documents,
        'active_menu': 'documents',
        'title': 'Danh sách tài liệu'
    }
    return render(request, 'document_list.html', context)


def document_detail(request, doc_id):
    document = get_object_or_404(Document, doc_id=doc_id)
    context = {
        'document': document,
        'active_menu': 'documents',
        'title': document.doc_name
    }
    return render(request, 'document_detail.html', context)


def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)

            # Nếu có file, xử lý loại file và dung lượng
            doc_file = request.FILES.get('doc_file')
            if doc_file:
                ext = os.path.splitext(doc_file.name)[1][1:].upper()
                document.file_type = ext
                document.file_size = f"{doc_file.size // 1024}KB"
                document.doc_file = doc_file

            document.save()
            messages.success(request, 'Tài liệu đã được thêm thành công!')
            return redirect('document_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = DocumentForm()

    return render(request, 'add_document.html', {
        'form': form,
        'active_menu': 'documents',
        'title': 'Thêm tài liệu mới'
    })


def edit_document(request, doc_id):
    document = get_object_or_404(Document, doc_id=doc_id)

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            updated_doc = form.save(commit=False)

            doc_file = request.FILES.get('doc_file')
            if doc_file:
                ext = os.path.splitext(doc_file.name)[1][1:].upper()
                updated_doc.file_type = ext
                updated_doc.file_size = f"{doc_file.size // 1024}KB"
                updated_doc.doc_file = doc_file

            updated_doc.save()
            messages.success(request, 'Tài liệu đã được cập nhật thành công!')
            return redirect('document_detail', doc_id=document.doc_id)
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = DocumentForm(instance=document)

    return render(request, 'edit_document.html', {
        'form': form,
        'document': document,
        'active_menu': 'documents',
        'title': f'Chỉnh sửa: {document.doc_name}'
    })


def delete_document(request, doc_id):
    document = get_object_or_404(Document, doc_id=doc_id)

    if request.method == 'POST':
        document_name = document.doc_name
        document.delete()
        messages.success(request, f'Tài liệu "{document_name}" đã được xóa thành công!')
        return redirect('document_list')

    return render(request, 'delete_document.html', {
        'document': document,
        'active_menu': 'documents',
        'title': f'Xóa tài liệu: {document.doc_name}'
    })


def download_document(request, doc_id):
    document = get_object_or_404(Document, doc_id=doc_id)

    if document.doc_file and hasattr(document.doc_file, 'url'):
        return redirect(document.doc_file.url)

    messages.error(request, 'File không tồn tại hoặc đã bị xóa.')
    return redirect('document_detail', doc_id=document.doc_id)
