from django.shortcuts import render, get_object_or_404
from english.models import DOCUMENT
from .forms import DocumentSearchForm

def materials_list(request):
    """Hiển thị danh sách tài liệu miễn phí (documents)"""
    documents = DOCUMENT.objects.all()
    search_form = DocumentSearchForm(request.GET or None)

    if search_form.is_valid():
        query = search_form.cleaned_data.get('search')
        if query:
            documents = documents.filter(doc_name__icontains=query)

    context = {
        'search_form': search_form,
        'documents': documents,
        'active_menu': 'materials',
        'title': 'Tài liệu miễn phí'
    }
    return render(request, 'materials_list.html', context)

