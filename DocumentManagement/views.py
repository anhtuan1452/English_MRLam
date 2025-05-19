from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from english.models import DOCUMENT
from .forms import DocumentForm
import os


def document_list(request):
    documents = DOCUMENT.objects.select_related('auth_user_id').all().order_by('-doc_id')
    context = {
        'documents': documents,
        'active_menu': 'documents',
        'title': 'Danh sách tài liệu',
    }
    return render(request, 'document_list.html', context)


def add_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc_file = request.FILES.get('doc_file')

            # Kiểm tra định dạng PDF
            if doc_file and not doc_file.name.lower().endswith('.pdf'):
                messages.error(request, 'Chỉ được phép tải lên tệp PDF.')
                return render(request, 'add_document.html', {
                    'form': form,
                    'active_menu': 'documents',
                    'title': 'Thêm tài liệu',
                })

            document = form.save(commit=False)
            document.save()
            messages.success(request, 'Tài liệu đã được thêm thành công!')
            return redirect('document_list')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = DocumentForm()

    return render(request, 'add_document.html', {
        'form': form,
        'active_menu': 'documents',
        'title': 'Thêm tài liệu',
    })

# Chi tiết và sửa tài liệu

def document_detail_edit(request, doc_id):
    document = get_object_or_404(DOCUMENT, pk=doc_id)

    if request.method == 'POST':
        if 'save' in request.POST:
            form = DocumentForm(request.POST, request.FILES, instance=document)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tài liệu đã được cập nhật thành công!')
                return redirect('document_list')
            else:
                messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
        elif 'delete' in request.POST:
            doc_name = document.doc_name
            document.delete()
            messages.success(request, f'Tài liệu "{doc_name}" đã được xóa thành công!')
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)
    file_name = os.path.basename(document.doc_file.name) if document.doc_file else None
    return render(request, 'document_detail_edit.html', {
        'form': form,
        'document': document,
        'doc_name': document.doc_name,
        'active_menu': 'documents',
        'title': f'Tài liệu - {document.doc_name}',
    })
