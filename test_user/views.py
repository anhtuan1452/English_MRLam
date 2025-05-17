# import json
# from collections import defaultdict
#
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect, get_object_or_404
# from django.views.decorators.http import require_POST
#
# from english.models import TEST, QUESTION, RESULT
#
# def home_test(request, test_id):
#     test = get_object_or_404(TEST, pk=test_id)
#     # Lấy test_description từ database
#     test_description = test.test_description
#
#     # Tách phần mô tả trước 'Bài kiểm tra gồm'
#     parts = test_description.split('Bài kiểm tra gồm')
#
#     # Kiểm tra nếu có phần mô tả sau 'Bài kiểm tra gồm'
#     if len(parts) > 1:
#         details = parts[1].strip()  # Lấy phần mô tả sau 'Bài kiểm tra gồm'
#
#         # Tách phần 'Listening:' và 'Reading:' từ phần mô tả
#         listening_part = ""
#         reading_part = ""
#
#         # Tìm phần 'Listening:'
#         if "Listening:" in details:
#             listening_part = details.split('Listening:', 1)[1].split('Reading:', 1)[0].strip()
#
#         # Tìm phần 'Reading:'
#         if "Reading:" in details:
#             reading_part = details.split('Reading:', 1)[1].strip()
#
#     else:
#         listening_part = ""
#         reading_part = ""
#
#     # Dựng từ điển chứa các phần đã tách
#     description_parts = {
#         'intro': parts[0].strip() if len(parts) > 0 else "",  # Phần trước 'Bài kiểm tra gồm'
#         'listening': listening_part,  # Phần mô tả 'Listening:'
#         'reading': reading_part,  # Phần mô tả 'Reading:'
#     }
#
#     # Truyền vào context để render vào template
#     context = {
#         'test': test,
#         'description_parts': description_parts,  # Truyền các phần đã tách vào context
#     }
#
#
#     return render(request, 'home_test.html', context)
#
# @login_required
# def test_page(request, test_id):
#     test = get_object_or_404(TEST, pk=test_id)
#     questions = QUESTION.objects.filter(test=test).select_related('question_media').order_by('question_id')
#
#     grouped_questions = defaultdict(list)
#     for q in questions:
#         key = q.question_media.questionmedia_id if q.question_media else None
#         grouped_questions[key].append(q)
#
#     grouped_questions = sorted(grouped_questions.items(), key=lambda item: min(q.question_id for q in item[1]))
#
#     # Tạo một list mới chứa (media_id, questions, start_index) để đánh số câu hỏi liên tục
#     start_index = 1
#     grouped_with_index = []
#     for media_id, qs in grouped_questions:
#         grouped_with_index.append((media_id, qs, start_index))
#         start_index += len(qs)
#
#     return render(request, 'tests.html', {
#         'test': test,
#         'grouped_questions': grouped_with_index,  # Truyền tuple (media_id, questions, start_index)
#     })
#
# def result_page(request, result_id):
#     result = get_object_or_404(RESULT, result_id=result_id)
#     test = result.test
#     questions = QUESTION.objects.filter(test=test)
#
#     user_answers = request.session.get('user_answers', {})
#     score = 0
#     detailed_result = []
#
#     for question in questions:
#         correct = question.correct_answer
#         user_ans = user_answers.get(str(question.question_id))
#         is_correct = user_ans == correct
#         if is_correct:
#             score += 1
#
#         # Lấy audio từ QUESTION_MEDIA nếu có
#         audio_url = None
#         if question.question_media and question.question_media.audio_file:
#             audio_url = question.question_media.audio_file.url
#
#         detailed_result.append({
#             'question': question.question_text,
#             'user_answer': user_ans,
#             'correct_answer': correct,
#             'is_correct': is_correct,
#             'audio': audio_url
#         })
#
#     total_questions = questions.count()
#     full_circle = 471.24
#     calculated_value = full_circle * (1 - score / total_questions) if total_questions > 0 else full_circle
#
#     context = {
#         'result': result,
#         'score': score,
#         'total_questions': total_questions,
#         'detailed_result': detailed_result,
#         'calculated_value': calculated_value,
#     }
#     return render(request, "result.html", context)
#
# @login_required
# @require_POST
# def submit_test(request, test_id):
#     test = get_object_or_404(TEST, pk=test_id)
#     questions = QUESTION.objects.filter(test=test)
#
#     user_answers = {}
#
#     # Giả sử form input có name="question_<question_id>"
#     for question in questions:
#         key = f"question_{question.question_id}"
#         answer = request.POST.get(key)
#         if answer is not None:
#             user_answers[str(question.question_id)] = answer
#
#     # Lưu đáp án user vào session
#     request.session['user_answers'] = user_answers
#
#     # Tạo record RESULT nếu cần, hoặc dùng cách khác
#     # result = RESULT.objects.create(user=request.user, test=test, ...)
#
#     # Ở đây giả sử bạn có result_id nào đó hoặc lấy ID mặc định
#     # Nếu không có, bạn có thể truyền test_id hoặc tạo mới RESULT
#     # Ví dụ tạm:
#     result = RESULT.objects.filter(user=request.user, test=test).last()
#     if not result:
#         result = RESULT.objects.create(user=request.user, test=test)
#
#     return redirect('result_page', result_id=result.result_id)
import json
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from english.models import TEST, QUESTION, RESULT


def home_test(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    # Xử lý tách test_description tương tự của bạn
    parts = test.test_description.split('Bài kiểm tra gồm')
    if len(parts) > 1:
        details = parts[1].strip()
        listening_part = ""
        reading_part = ""
        if "Listening:" in details:
            listening_part = details.split('Listening:', 1)[1].split('Reading:', 1)[0].strip()
        if "Reading:" in details:
            reading_part = details.split('Reading:', 1)[1].strip()
    else:
        listening_part = ""
        reading_part = ""

    description_parts = {
        'intro': parts[0].strip() if len(parts) > 0 else "",
        'listening': listening_part,
        'reading': reading_part,
    }

    context = {
        'test': test,
        'description_parts': description_parts,
    }

    return render(request, 'home_test.html', context)


@login_required
def test_page(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    questions = QUESTION.objects.filter(test=test).select_related('question_media').order_by('question_id')

    grouped_questions = defaultdict(list)
    for q in questions:
        key = q.question_media.questionmedia_id if q.question_media else None
        grouped_questions[key].append(q)

    grouped_questions = sorted(grouped_questions.items(), key=lambda item: min(q.question_id for q in item[1]))

    start_index = 1
    grouped_with_index = []
    for media_id, qs in grouped_questions:
        grouped_with_index.append((media_id, qs, start_index))
        start_index += len(qs)

    return render(request, 'tests.html', {
        'test': test,
        'grouped_questions': grouped_with_index,
    })


@login_required
@require_POST
def submit_test(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    questions = QUESTION.objects.filter(test=test)

    user_answers = {}
    for question in questions:
        answer = request.POST.get(f"answer_{question.question_id}")
        if answer is not None:
            user_answers[str(question.question_id)] = answer

    score = 0
    total_questions = questions.count()
    for q in questions:
        if user_answers.get(str(q.question_id)) == q.correct_answer:
            score += 1

    user_answer_json = json.dumps(user_answers)

    result = RESULT.objects.create(
        acc=request.user,
        test=test,
        score=score,
        total_questions=total_questions,
        user_answer=user_answer_json,
        create_at=timezone.now()  # nếu bạn có trường này
    )

    return redirect('result_page', result_id=result.result_id)

@login_required
def result_page(request, result_id):
    result = get_object_or_404(RESULT, result_id=result_id)
    test = result.test
    questions = QUESTION.objects.filter(test=test)

    # Lấy user_answer JSON từ database, chuyển về dict
    try:
        user_answers = json.loads(result.user_answer) if result.user_answer else {}
    except json.JSONDecodeError:
        user_answers = {}

    score = 0
    detailed_result = []

    for question in questions:
        correct = question.correct_answer
        user_ans = user_answers.get(str(question.question_id))
        is_correct = user_ans == correct
        if is_correct:
            score += 1

        audio_url = None
        if question.question_media and question.question_media.audio_file:
            audio_url = question.question_media.audio_file.url

        detailed_result.append({
            'question': question.question_text,
            'user_answer': user_ans,
            'correct_answer': correct,
            'is_correct': is_correct,
            'audio': audio_url
        })

    total_questions = questions.count()
    full_circle = 471.24
    calculated_value = full_circle * (1 - score / total_questions) if total_questions > 0 else full_circle

    context = {
        'result': result,
        'score': score,
        'total_questions': total_questions,
        'detailed_result': detailed_result,
        'calculated_value': calculated_value,
    }
    return render(request, "result.html", context)