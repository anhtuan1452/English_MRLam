from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from english.models import LESSON, COURSE, LESSON_DETAIL
from .forms import CombinedLessonForm
import os

# Danh sách tài liệu (LESSON)
def document_list(request):
    lessons = LESSON.objects.select_related('course').all().order_by('-lesson_id')
    context = {
        'documents': lessons,
        'active_menu': 'documents',
        'title': 'Danh sách tài liệu',
    }
    return render(request, 'document_list.html', context)

# Thêm mới tài liệu (LESSON + LESSON_DETAIL)
def add_document(request):
    if request.method == 'POST':
        form = CombinedLessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson_file = request.FILES.get('lesson_file')
            exercise_file = request.FILES.get('exercise_file')

            # Kiểm tra định dạng PDF
            for file in [lesson_file, exercise_file]:
                if file and not file.name.lower().endswith('.pdf'):
                    messages.error(request, 'Chỉ được phép tải lên tệp PDF.')
                    return render(request, 'add_document.html', {
                        'form': form,
                        'active_menu': 'documents',
                        'title': 'Thêm tài liệu',
                    })

            form.save()
            messages.success(request, 'Tài liệu đã được thêm thành công!')
            return redirect('document_list')
        else:
            messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = CombinedLessonForm()

    return render(request, 'add_document.html', {
        'form': form,
        'active_menu': 'documents',
        'title': 'Thêm tài liệu',
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from english.models import LESSON, COURSE, LESSON_DETAIL
from .forms import CombinedLessonForm
import os

def document_detail_edit(request, lesson_id):
    lesson = get_object_or_404(LESSON, pk=lesson_id)

    if request.method == 'POST':
        if 'save' in request.POST:
            form = CombinedLessonForm(request.POST, request.FILES, lesson_instance=lesson)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tài liệu đã được cập nhật thành công!')
                return redirect('/document_management/')
            else:
                messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
        elif 'delete' in request.POST:
            lesson_name = lesson.lesson_name
            lesson.delete()
            messages.success(request, f'Tài liệu "{lesson_name}" đã được xóa thành công!')
            return redirect('/document_management/')
        else:

            form = CombinedLessonForm(lesson_instance=lesson)
    else:
        form = CombinedLessonForm(lesson_instance=lesson)

    return render(request, 'document_detail_edit.html', {
        'form': form,
        'document': lesson,
        'lesson_name': lesson.lesson_name,
        'active_menu': 'documents',
        'title': f'Tài liệu - {lesson.course.course_name} - {lesson.lesson_name}',
    })
