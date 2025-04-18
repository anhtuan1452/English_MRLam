from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from english.models import DOCUMENT
from .forms import DocumentSearchForm


def materials_list(request):
    """Hiển thị danh sách tài liệu miễn phí (documents)"""

    documents = DOCUMENT.objects.all()
    search_form = DocumentSearchForm(request.GET)

    if search_form.is_valid() and search_form.cleaned_data['search']:
        query = search_form.cleaned_data['search']
        documents = documents.filter(doc_name__icontains=query)

    context = {
        'search_form': search_form,
        'documents': documents,
        'active_menu': 'materials',
        'title': 'Tài liệu miễn phí'
    }
    return render(request, 'materials_list.html', context)


def materials_detail(request, doc_id):
    """Chi tiết tài liệu"""

    document = get_object_or_404(DOCUMENT, doc_id=doc_id)

    context = {
        'document': document,
        'active_menu': 'materials',
        'title': document.doc_name
    }
    return render(request, 'materials_detail.html', context)
