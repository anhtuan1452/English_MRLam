from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from english.models import LESSON, COURSE,LESSON_DETAIL
from .forms import CombinedLessonForm  # Bạn sẽ tạo form mới này
import os

def document_list(request):
    lessons = LESSON.objects.select_related('course').all().order_by('-lesson_id')
    context = {
        'documents': lessons,
        'active_menu': 'documents',
        'title': 'Danh sách tài liệu'
    }
    return render(request, 'document_list.html', context)


def add_document(request):
    if request.method == 'POST':
        form = CombinedLessonForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES.get('lesson_file')
            if file:
                ext = os.path.splitext(file.name)[1].lower()
                if ext != '.pdf':
                    messages.error(request, 'Chỉ được phép tải lên tệp PDF.')
                    return render(request, 'add_document.html', {
                        'form': form,
                        'active_menu': 'documents',
                        'title': 'Thêm tài liệu'
                    })

            # Gọi save() để xử lý tạo LESSON + LESSON_DETAIL
            form.save()
            messages.success(request, 'Tài liệu đã được thêm thành công!')
            return redirect('document_list')
        else:
            messages.error(request, 'Có lỗi xảy ra. Vui lòng kiểm tra lại thông tin.')
    else:
        form = CombinedLessonForm()

    return render(request, 'add_document.html', {
        'form': form,
        'active_menu': 'documents',
        'title': 'Thêm tài liệu'
    })


def delete_document(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)
    if request.method == 'POST':
        lesson_name = lesson.course.course_name
        lesson.delete()
        messages.success(request, f'Tài liệu từ khóa học "{lesson_name}" đã được xóa thành công!')
        return redirect('document_list')

    return render(request, 'delete_document.html', {
        'lesson': lesson,
        'active_menu': 'documents',
        'title': f'Xóa tài liệu: {lesson.course.course_name}'
    })


def download_document(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)

    if lesson.lesson_file and hasattr(lesson.lesson_file, 'url'):
        return redirect(lesson.lesson_file.url)

    messages.error(request, 'File không tồn tại hoặc đã bị xóa.')
    return redirect('document_list')

def document_detail(request, lesson_id):
    lesson = get_object_or_404(LESSON, lesson_id=lesson_id)

    # Lấy lesson_detail đầu tiên nếu có
    lesson_detail = LESSON_DETAIL.objects.filter(lesson=lesson).first()

    context = {
        'document': lesson,
        'lesson_detail': lesson_detail
    }
    return render(request, 'document_detail.html', context)
def edit_document(request, doc_id):
    lesson = get_object_or_404(LESSON, pk=doc_id)
    detail = get_object_or_404(LESSON_DETAIL, lesson=lesson)

    if request.method == 'POST':
        form = CombinedLessonForm(request.POST, request.FILES, lesson_instance=lesson, detail_instance=detail)
        if form.is_valid():
            form.save()
            return redirect('document_detail', lesson_id=doc_id)
    else:
        form = CombinedLessonForm(lesson_instance=lesson, detail_instance=detail)

    return render(request, 'edit_document.html', {
        'form': form,
        'document': lesson,
        'file_name': lesson.lesson_file.name.split('/')[-1]
    })