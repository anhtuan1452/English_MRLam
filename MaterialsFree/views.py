# MaterialsFree/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import DocumentSearchForm
from Document.models import Document  # Adjust this import to match your actual model location


def materials_list(request):
    """View to display all free materials/documents"""
    documents = Document.objects.all()
    search_form = DocumentSearchForm(request.GET)

    # Handle search
    if search_form.is_valid() and search_form.cleaned_data['search']:
        query = search_form.cleaned_data['search']
        documents = documents.filter(doc_name__icontains=query)

    # Group documents by category (for display purposes)
    # Since we don't have a category field, we'll categorize based on document name
    grammar_docs = documents.filter(
        Q(doc_name__icontains='grammar') |
        Q(doc_name__icontains='thì') |
        Q(doc_name__icontains='tense')
    )
    vocabulary_docs = documents.filter(
        Q(doc_name__icontains='vocabulary') |
        Q(doc_name__icontains='từ vựng')
    )
    speaking_docs = documents.filter(
        Q(doc_name__icontains='speaking') |
        Q(doc_name__icontains='nói')
    )
    listening_docs = documents.filter(
        Q(doc_name__icontains='listening') |
        Q(doc_name__icontains='nghe')
    )

    # If a document appears in multiple categories, prioritize the first match
    used_ids = set()
    for doc_list in [grammar_docs, vocabulary_docs, speaking_docs, listening_docs]:
        doc_ids = set(doc_list.values_list('doc_id', flat=True))
        doc_list = doc_list.exclude(doc_id__in=used_ids)
        used_ids.update(doc_ids)

    # Other documents that don't fit into the above categories
    other_docs = documents.exclude(doc_id__in=used_ids)

    context = {
        'search_form': search_form,
        'grammar_docs': grammar_docs[:4],  # Limit to 4 items per category
        'vocabulary_docs': vocabulary_docs[:4],
        'speaking_docs': speaking_docs[:4],
        'listening_docs': listening_docs[:4],
        'other_docs': other_docs[:4],
        'active_menu': 'materials',
        'title': 'Tài liệu'
    }
    return render(request, 'MaterialsFree/materials_list.html', context)


def material_detail(request, doc_id):
    """View to display details of a specific document"""
    document = get_object_or_404(Document, doc_id=doc_id)

    # For demonstration, we'll create some dummy content based on the document name
    if 'present tense' in document.doc_name.lower() or 'hiện tại đơn' in document.doc_name.lower():
        content_type = 'present_tense'
    elif 'past tense' in document.doc_name.lower() or 'quá khứ' in document.doc_name.lower():
        content_type = 'past_tense'
    else:
        content_type = 'general'

    context = {
        'document': document,
        'content_type': content_type,
        'active_menu': 'materials',
        'title': document.doc_name
    }
    return render(request, 'MaterialsFree/material_detail.html', context)