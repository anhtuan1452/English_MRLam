from django.shortcuts import render, get_object_or_404
from .models import Document, Category


def materials_list(request):
    documents = Document.objects.all()
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        documents = documents.filter(category=category)

    context = {
        'documents': documents,
        'categories': categories,
    }
    # Print for debugging
    print(f"Found {documents.count()} documents")
    return render(request, 'materials_list.html', context)


def materials_detail(request, slug):
    document = get_object_or_404(Document, slug=slug)
    related_documents = Document.objects.filter(category=document.category).exclude(id=document.id)[:4]

    context = {
        'document': document,
        'related_documents': related_documents,
    }
    return render(request, 'MaterialsFree/materials_detail.html', context)

