from django.shortcuts import render, redirect,get_object_or_404
from english.models import  RESULT, TEST, QUESTION, QUESTION_MEDIA
from .forms import TestForm, QuestionForm, CustomQuestionForm, QuestionMediaForm
from django.forms import formset_factory
from collections import OrderedDict, defaultdict


# Create your views here.
def test_list(request):
    query = request.GET.get('q', '')  # Lấy từ khóa tìm kiếm từ query string
    if query:
        tests = TEST.objects.filter(test_name__icontains=query)
    else:
        tests = TEST.objects.all()
    return render(request, 'test_list.html', {'tests': tests, 'query': query})


def test_delete(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)

    if request.method == 'POST':
        test.delete()
        # return redirect('results')
    return redirect('admin_test_list')

def test_detail_view(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    questions = QUESTION.objects.filter(test=test).select_related('question_media')

    media_groups = OrderedDict()
    question_counter = 1

    for question in questions:
        media = question.question_media
        if media not in media_groups:
            media_groups[media] = []
        question.display_number = question_counter
        question_counter += 1
        media_groups[media].append(question)

    return render(request, 'test_detail.html', {
        'test': test,
        'media_groups': media_groups.items(),  # Trả về list of tuples (media, [questions])
    })

def test_edit_view(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    questions = QUESTION.objects.filter(test=test).select_related('question_media')

    # Nhóm câu hỏi theo question_media
    question_groups_dict = defaultdict(list)
    for question in questions:
        question_groups_dict[question.question_media_id].append(question)

    question_groups = []

    if request.method == 'POST':
        test_form = TestForm(request.POST, instance=test)
        all_valid = test_form.is_valid()

        for group_index, (media_id, group_questions) in enumerate(question_groups_dict.items()):
            media_prefix = f'media{group_index}'
            question_forms = []
            valid_group = True

            # Lấy media (có thể là None)
            media_instance = group_questions[0].question_media or QUESTION_MEDIA()
            media_form = QuestionMediaForm(request.POST, request.FILES, instance=media_instance, prefix=media_prefix)

            if media_form.is_valid():
                media = media_form.save(commit=False)
                uploaded_audio = request.FILES.get(f'{media_prefix}-audio_file')
                if uploaded_audio:
                    if media.audio_file and uploaded_audio.name != media.audio_file.name:
                        media.audio_file.delete(save=False)
                    media.audio_file = uploaded_audio
                media.save()
            else:
                all_valid = False
                valid_group = False
                print(f"❌ Media form lỗi nhóm {group_index}: {media_form.errors}")

            for q_index, question in enumerate(group_questions):
                prefix = f'q{question.question_id}'
                question_form = CustomQuestionForm(request.POST, instance=question, prefix=prefix)

                if question_form.is_valid():
                    q = question_form.save(commit=False)
                    q.test = test
                    q.question_media = media_instance
                    q.save()
                else:
                    # ✅ Gán lại giá trị các đáp án để giữ hiển thị nếu form lỗi
                    question_form.instance.answer = {
                        'A': request.POST.get(f'{prefix}-answer_a', ''),
                        'B': request.POST.get(f'{prefix}-answer_b', ''),
                        'C': request.POST.get(f'{prefix}-answer_c', ''),
                        'D': request.POST.get(f'{prefix}-answer_d', '')
                    }
                    all_valid = False
                    valid_group = False
                    print(f"❌ Câu hỏi lỗi: {question_form.errors}")

                question_forms.append(question_form)

            question_groups.append({
                'media_form': media_form,
                'question_forms': question_forms
            })

        if all_valid:
            test_form.save()
            return redirect('admin_test_details', test_id=test.test_id)

    else:
        test_form = TestForm(instance=test)

        for group_index, (media_id, group_questions) in enumerate(question_groups_dict.items()):
            media_instance = group_questions[0].question_media or QUESTION_MEDIA()
            media_form = QuestionMediaForm(instance=media_instance, prefix=f'media{group_index}')
            question_forms = [
                CustomQuestionForm(instance=q, prefix=f'q{q.question_id}') for q in group_questions
            ]
            question_groups.append({
                'media_form': media_form,
                'question_forms': question_forms
            })

    return render(request, 'test_edit.html', {
        'test': test,
        'test_form': test_form,
        'question_groups': question_groups
    })

from django.forms import formset_factory

# def test_add_view(request):
#     QuestionFormSet = formset_factory(CustomQuestionForm, extra=0)
#     MediaFormSet = formset_factory(QuestionMediaForm, extra=0)
#
#     if request.method == 'POST':
#         question_formset = QuestionFormSet(request.POST)
#         media_formset = MediaFormSet(request.POST, request.FILES)
#         test_form = TestForm(request.POST)
#
#         if test_form.is_valid() and question_formset.is_valid() and media_formset.is_valid():
#             test = test_form.save()
#
#             for q_form, m_form in zip(question_formset, media_formset):
#                 media = m_form.save(commit=False)
#                 if m_form.cleaned_data.get('audio_file') or m_form.cleaned_data.get('paragraph'):
#                     media.save()
#                 else:
#                     media = None
#
#                 question = q_form.save(commit=False)
#                 question.test = test
#                 question.question_media = media
#                 question.save()
#
#             return redirect('admin_test_list')
#
#     else:
#         test_form = TestForm()
#         question_formset = QuestionFormSet()
#         media_formset = MediaFormSet()
#
#     return render(request, 'test_add.html', {
#         'test_form': test_form,
#         'question_formset': zip(question_formset, media_formset),
#         'question_total': len(question_formset)
#     })

def list_result_view(request):
    query = request.GET.get('q', '').strip()
    results = RESULT.objects.select_related('test', 'acc')

    if query:
        results = results.filter(
            acc__first_name__icontains=query
        ) | results.filter(
            acc__last_name__icontains=query
        )

    data = []
    for index, result in enumerate(results, start=1):
        data.append({
            'stt': index,
            'id': result.result_id,
            'score': result.score,
            'total_questions': result.total_questions,
            'create_at': result.create_at,
            'test_name': result.test.test_name,
            'full_name': f"{result.acc.last_name} {result.acc.first_name}",
        })
    context = {
            'test_results': data,
            'page_title': 'Bài kiểm tra',
            'section_title': 'Kết quả',
            'query': query
        }
    return render(request, 'test_results.html', context)
def result_delete(request, result_id):
    result = get_object_or_404(RESULT, result_id=result_id)

    if request.method == 'POST':
        result.delete()
        # return redirect('results')
    return redirect('results')



from django.shortcuts import render, redirect
from django.contrib import messages
from english.models import TEST, QUESTION, QUESTION_MEDIA
from .forms import TestForm

def test_add_view(request):
    if request.method == 'POST':
        test_form = TestForm(request.POST)
        if test_form.is_valid():
            test = test_form.save()

            # Tìm tất cả nhóm media trong POST
            media_indexes = set()
            for key in request.POST:
                if key.startswith('media-') and '-q-' not in key:
                    try:
                        media_indexes.add(int(key.split('-')[1]))
                    except:
                        pass

            media_has_question = True

            for i in sorted(media_indexes):
                # Lấy dữ liệu media
                audio = request.FILES.get(f'media-{i}-audio_file')
                paragraph = request.POST.get(f'media-{i}-paragraph')

                if not audio and not paragraph:
                    media = None
                else:
                    media = QUESTION_MEDIA.objects.create(audio_file=audio, paragraph=paragraph)

                # Lấy các câu hỏi cho nhóm media i
                question_indexes = []
                for key in request.POST:
                    if key.startswith(f'media-{i}-q-') and key.endswith('-question_text'):
                        try:
                            q_index = int(key.split('-')[3])
                            question_indexes.append(q_index)
                        except:
                            pass

                if not question_indexes:
                    media_has_question = False
                    messages.error(request, f'Nhóm Media {i+1} không có câu hỏi nào.')
                    break

                for j in sorted(question_indexes):
                    question_text = request.POST.get(f'media-{i}-q-{j}-question_text')
                    correct_answer = request.POST.get(f'media-{i}-q-{j}-correct_answer')
                    answer = {
                        'A': request.POST.get(f'media-{i}-q-{j}-answer_a'),
                        'B': request.POST.get(f'media-{i}-q-{j}-answer_b'),
                        'C': request.POST.get(f'media-{i}-q-{j}-answer_c'),
                        'D': request.POST.get(f'media-{i}-q-{j}-answer_d'),
                    }
                    QUESTION.objects.create(
                        test=test,
                        question_text=question_text,
                        correct_answer=correct_answer,
                        answer=answer,
                        question_media=media
                    )

            if not media_has_question:
                test.delete()  # rollback
                return render(request, 'test_add.html', {'test_form': test_form})

            return redirect('admin_test_list')

        else:
            messages.error(request, 'Form bài kiểm tra không hợp lệ.')

    else:
        test_form = TestForm()

    return render(request, 'test_add.html', {
        'test_form': test_form
    })