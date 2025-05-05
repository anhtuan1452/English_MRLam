from django.shortcuts import render, get_object_or_404
from django.http import Http404
from english.models import DOCUMENT
from .forms import DocumentSearchForm


def materials_list(request):
    """Hiển thị danh sách tài liệu miễn phí (documents)"""
    documents = DOCUMENT.objects.all()
    search_form = DocumentSearchForm(request.GET)

    if search_form.is_valid() and search_form.cleaned_data['search']:
        query = search_form.cleaned_data['search']
        documents = documents.filter(doc_name__icontains=query)

    # Add document URLs to each document
    for doc in documents:
        if doc.doc_file:
            # Google Drive link is already a URL
            doc.file_url = doc.doc_file
        else:
            doc.file_url = None

    context = {
        'search_form': search_form,
        'documents': documents,
        'active_menu': 'materials',
        'title': 'Tài liệu miễn phí'
    }
    return render(request, 'materials_list.html', context)


def materials_detail(request, doc_id):
    document = get_object_or_404(DOCUMENT, pk=doc_id)

    # Kiểm tra nếu tài liệu có link Google Drive, xử lý thêm
    if 'drive.google.com' in document.doc_file:
        file_url = document.doc_file
    else:
        # Nếu file không phải link Google Drive, kiểm tra xem file có tồn tại trong server không
        file_url = None

    return render(request, 'materials_detail.html', {
        'document': document,
        'file_url': file_url
    })