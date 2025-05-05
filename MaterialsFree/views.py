from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from english.models import DOCUMENT
from .forms import DocumentSearchForm
from django.conf import settings
import os


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
            doc.file_url = os.path.join(settings.MEDIA_URL, str(doc.doc_file))
        else:
            doc.file_url = None

    context = {
        'search_form': search_form,
        'documents': documents,
        'active_menu': 'materials',
        'title': 'Tài liệu miễn phí'
    }
    return render(request, 'materials_list.html', context)


# views.py

from django.shortcuts import render, get_object_or_404
from django.conf import settings
from english.models import DOCUMENT

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
import os


def materials_detail(request, doc_id):
    document = get_object_or_404(DOCUMENT, pk=doc_id)

    # Debug thông tin
    print(f"File name in DB: {document.doc_file.name}")
    print(f"Full path: {document.doc_file.path}")
    print(f"File exists: {os.path.exists(document.doc_file.path)}")
    print(f"File URL: {document.doc_file.url}")

    if not document.doc_file:
        raise Http404("Document không có file đính kèm")

    if not os.path.exists(document.doc_file.path):
        raise Http404(f"File không tồn tại tại: {document.doc_file.path}")

    return render(request, 'materials_detail.html', {
        'document': document,
        'file_url': document.doc_file.url
    })