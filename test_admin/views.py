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

def test_add_view(request):
    QuestionFormSet = formset_factory(CustomQuestionForm, extra=0)
    MediaFormSet = formset_factory(QuestionMediaForm, extra=0)

    if request.method == 'POST':
        question_formset = QuestionFormSet(request.POST)
        media_formset = MediaFormSet(request.POST, request.FILES)
        test_form = TestForm(request.POST)

        if test_form.is_valid() and question_formset.is_valid() and media_formset.is_valid():
            test = test_form.save()

            for q_form, m_form in zip(question_formset, media_formset):
                media = m_form.save(commit=False)
                if m_form.cleaned_data.get('audio_file') or m_form.cleaned_data.get('paragraph'):
                    media.save()
                else:
                    media = None

                question = q_form.save(commit=False)
                question.test = test
                question.question_media = media
                question.save()

            return redirect('admin_test_list')

    else:
        test_form = TestForm()
        question_formset = QuestionFormSet()
        media_formset = MediaFormSet()

    return render(request, 'test_add.html', {
        'test_form': test_form,
        'question_formset': zip(question_formset, media_formset),
        'question_total': len(question_formset)
    })



def test_add(request):
    if request.method == 'POST':
        test_name = request.POST.get('test_name')
        time_limit = request.POST.get('time_limit')
        test = TEST.objects.create(test_name=test_name, duration=f'00:{time_limit}:00')  # chuyển đổi sang kiểu TimeField nếu cần

        num_questions = int(request.POST.get('num_questions', 0))

        for i in range(num_questions):
            question_text = request.POST.get(f'question_text_{i}')
            audio_url = request.POST.get(f'media_audio_url_{i}', '').strip()
            paragraph = request.POST.get(f'media_paragraph_{i}', '').strip()

            media = None
            if audio_url or paragraph:
                media = QUESTION_MEDIA.objects.create(audio_file=audio_url, paragraph=paragraph)

            answer_choices = []
            for j in range(int(request.POST.get(f'num_choices_{i}', 0))):
                answer_choices.append(request.POST.get(f'choice_{i}_{j}', ''))

            correct_index = request.POST.get(f'correct_{i}')
            correct_answer = chr(65 + int(correct_index)) if correct_index else ''

            question = QUESTION.objects.create(
                test=test,
                question_text=question_text,
                answer=';'.join(answer_choices),
                correct_answer=correct_answer,
                question_media=media
            )

        return redirect('admin_ql_test')

    return render(request, 'test_add1.html')

QuestionFormSet = formset_factory(CustomQuestionForm, extra=1, can_delete=True)

def test_create(request):
    if request.method == 'POST':
        test_form = TestForm(request.POST)
        question_formset = QuestionFormSet(request.POST, prefix='questions')

        if test_form.is_valid() and question_formset.is_valid():
            # Lưu bài kiểm tra
            test = test_form.save()

            # Lưu các câu hỏi
            for form in question_formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    question = form.save(commit=False)

                    audio = form.cleaned_data.get('link_audio')
                    paragraph = form.cleaned_data.get('paragraph')
                    if audio or paragraph:
                        media = QUESTION_MEDIA.objects.create(audio_file=audio or '', paragraph=paragraph or '')
                        question.question_media = media

                    question.test = test
                    question.save()

            return redirect('admin_test_details', test_id=test.test_id)
        else:
            print("Test Form Errors:", test_form.errors.as_json())
            print("Question Formset Errors:", question_formset.errors)
            print("POST Data:", request.POST)
    else:
        test_form = TestForm()
        question_formset = QuestionFormSet(prefix='questions')

    return render(request, 'test_create.html', {
        'test_form': test_form,
        'question_formset': question_formset,
    })

# ------------
# Đã đúng còn phần test add

def list_result_view(request):
    results = RESULT.objects.all().select_related('test', 'acc')

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
        }
    return render(request, 'test_results.html', context)
def result_delete(request, result_id):
    result = get_object_or_404(RESULT, result_id=result_id)

    if request.method == 'POST':
        result.delete()
        # return redirect('results')
    return redirect('results')
