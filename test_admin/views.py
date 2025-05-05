from django.shortcuts import render, redirect,get_object_or_404
from english.models import  RESULT, TEST, QUESTION, QUESTION_MEDIA
from .forms import TestForm, QuestionForm, CustomQuestionForm, QuestionMediaForm
from django.forms import formset_factory
from collections import OrderedDict


# Create your views here.
def test_list(request):
    query = request.GET.get('q', '')  # Lấy từ khóa tìm kiếm từ query string
    if query:
        tests = TEST.objects.filter(test_name__icontains=query)
    else:
        tests = TEST.objects.all()
    return render(request, 'test_list.html', {'tests': tests, 'query': query})


# def test_list(request):
#     tests = TEST.objects.all()  # Get all tests from the database
#     return render(request, 'test_list.html', {'tests': tests})

def test_delete(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)

    if request.method == 'POST':
        test.delete()
        # return redirect('results')
    return redirect('admin_test_list')

from collections import defaultdict

# def test_detail(request, test_id):
#     test = get_object_or_404(TEST, pk=test_id)
#     questions = QUESTION.objects.filter(test=test).select_related('question_media')
#
#     test_form = TestForm(instance=test)
#
#     # Nhóm các câu hỏi theo question_media
#     grouped_questions = defaultdict(list)
#     for q in questions:
#         form = QuestionForm(instance=q)
#         form.choices = q.answer.split(';') if q.answer else []
#         grouped_questions[q.question_media].append(form)
#
#     return render(request, 'test_detail.html', {
#         'test_form': test_form,
#         'grouped_questions': grouped_questions.items(),  # Trả về list of (media, [form, form...])
#         'test': test,
#         # 'MEDIA_URL': settings.MEDIA_URL
#     })

def test_detail(request, test_id):
    # Lấy bài kiểm tra theo test_id
    test = get_object_or_404(TEST, pk=test_id)

    # Lấy tất cả các câu hỏi thuộc bài kiểm tra này
    questions = QUESTION.objects.filter(test=test)

    # Nếu form được gửi lên, bạn có thể xử lý ở đây (tùy vào logic của bạn)
    if request.method == 'POST':
        test_form = TestForm(request.POST, instance=test)
        question_forms = [QuestionForm(request.POST, instance=q) for q in questions]

        if all(form.is_valid() for form in question_forms):
            # Lưu lại các câu trả lời, đáp án ở đây (nếu cần)
            for form in question_forms:
                form.save()
            # Thực hiện thêm logic sau khi lưu dữ liệu, như chuyển hướng hoặc thông báo thành công
    else:
        # Khởi tạo form mặc định cho test và câu hỏi
        test_form = TestForm(instance=test)
        question_forms = []
        for q in questions:
            form = QuestionForm(instance=q)
            form.choices = q.answer.split(';')
            question_forms.append({
                'form': form,
                'media':q.question_media
            })

    # Trả về template với dữ liệu của bài kiểm tra và câu hỏi
    return render(request, 'test_detail.html', {
        'test_form': test_form,
        'question_forms': question_forms,
        'test': test,
    })

def test_edit(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    questions = QUESTION.objects.filter(test=test)

    if request.method == 'POST':
        test_form = TestForm(request.POST, instance=test)
        question_forms = [CustomQuestionForm(request.POST, prefix=str(q.pk), instance=q) for q in questions]

        if test_form.is_valid() and all(qf.is_valid() for qf in question_forms):
            test_form.save()
            for qf in question_forms:
                qf.save()
            return redirect('admin_test_details', test_id=test.test_id)  # Hoặc trang khác tùy ý
        else:
            # In lỗi form ra để kiểm tra
            # In lỗi form ra để kiểm tra
            print("Test Form Errors:", test_form.errors)
            for form in question_forms:
                print(f"Question Form Errors for question {form.instance.pk}: {form.errors}")
            print("POST Data:", request.POST)
    else:
        test_form = TestForm(instance=test)
        question_forms = [CustomQuestionForm(instance=q, prefix=str(q.pk)) for q in questions]

    return render(request, 'test_edit.html', {
        'test_form': test_form,
        'question_forms': question_forms,
        'test': test,
    })
# def test_edit(request, test_id):
#     test = get_object_or_404(TEST, pk=test_id)
#     questions = QUESTION.objects.filter(test=test).select_related('question_media')
#
#     # Group theo media
#     media_dict = OrderedDict()
#     question_forms = []
#
#     for q in questions:
#         question_forms.append(CustomQuestionForm(
#             request.POST or None,
#             instance=q,
#             prefix=f"q_{q.pk}"
#         ))
#
#         media = q.question_media
#         if media and media.pk not in media_dict:
#             media_dict[media.pk] = QuestionMediaForm(
#                 request.POST or None,
#                 instance=media,
#                 prefix=f"m_{media.pk}"
#             )
#
#     test_form = TestForm(request.POST or None, instance=test)
#
#     if request.method == 'POST':
#         valid = (
#             test_form.is_valid()
#             and all(qf.is_valid() for qf in question_forms)
#             and all(mf.is_valid() for mf in media_dict.values())
#         )
#         if valid:
#             test_form.save()
#             for qf in question_forms:
#                 qf.save()
#             for mf in media_dict.values():
#                 mf.save()
#             return redirect('admin_test_details', test_id=test.test_id)
#         else:
#             print("Form lỗi:", test_form.errors)
#             for f in question_forms:
#                 print("Q error:", f.errors)
#             for f in media_dict.values():
#                 print("Media error:", f.errors)
#
#     return render(request, 'test_edit.html', {
#         'test': test,
#         'test_form': test_form,
#         'question_forms': question_forms,
#         'media_forms': media_dict.values(),
#     })

# def test_add(request):
#     if request.method == 'POST':
#         # Lấy thông tin từ form
#         test_name = request.POST.get('test_name')
#         time_limit = request.POST.get('time_limit')
#
#         # Tạo bài kiểm tra mới
#         test = TEST.objects.create(test_name=test_name, time=time_limit)
#
#         # Lưu câu hỏi
#         for i in range(int(request.POST.get('num_questions'))):
#             question_text = request.POST.get(f'question_text_{i}')
#             question = QUESTION.objects.create(test=test, question_text=question_text)
#             # Thêm các lựa chọn câu hỏi
#             for j in range(int(request.POST.get(f'num_choices_{i}'))):
#                 choice_text = request.POST.get(f'choice_{i}_{j}')
#                 is_correct = 'correct' in request.POST.getlist(f'correct_{i}')
#                 # Lưu các lựa chọn
#                 question.choices.create(choice_text=choice_text, correct=is_correct)
#
#         return redirect('admin_ql_test')  # Redirect về trang danh sách bài kiểm tra
#
#     return render(request, 'test_add.html')

# def test_create(request):
#     QuestionFormSet = modelformset_factory(QUESTION, form=CustomQuestionForm, extra=4, can_delete=False)
#
#     if request.method == 'POST':
#         test_form = TestForm(request.POST)
#         formset = QuestionFormSet(request.POST, queryset=QUESTION.objects.none())
#
#         if test_form.is_valid() and formset.is_valid():
#             test = test_form.save()
#
#             for form in formset:
#                 question = form.save(commit=False)
#                 question.test = test  # Gán foreign key
#                 question.save()
#
#             return redirect('admin_test_list')  # hoặc trang chi tiết bài kiểm tra
#
#     else:
#         test_form = TestForm()
#         formset = QuestionFormSet(queryset=QUESTION.objects.none())
#
#     return render(request, 'test_create.html', {
#         'test_form': test_form,
#         'question_forms': formset
#     })
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

    return render(request, 'test_add.html')

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


def list_result_view(request):
    results = RESULT.objects.all().select_related('test_id', 'acc_id')

    data = []
    for index, result in enumerate(results, start=1):
        data.append({
            'stt': index,
            'id': result.result_id,
            'score': result.score,
            'total_questions': result.total_questions,
            'create_at': result.create_at,
            'test_name': result.test_id.test_name,
            'full_name': f"{result.acc_id.last_name} {result.acc_id.first_name}",
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
