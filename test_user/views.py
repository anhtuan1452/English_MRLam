from django.shortcuts import render, redirect, get_object_or_404

from english.models import TEST, QUESTION, RESULT

def home_test(request, test_id):
    test = get_object_or_404(TEST, pk=test_id)
    # Lấy test_description từ database
    test_description = test.test_description

    # Tách phần mô tả trước 'Bài kiểm tra gồm'
    parts = test_description.split('Bài kiểm tra gồm')

    # Kiểm tra nếu có phần mô tả sau 'Bài kiểm tra gồm'
    if len(parts) > 1:
        details = parts[1].strip()  # Lấy phần mô tả sau 'Bài kiểm tra gồm'

        # Tách phần 'Listening:' và 'Reading:' từ phần mô tả
        listening_part = ""
        reading_part = ""

        # Tìm phần 'Listening:'
        if "Listening:" in details:
            listening_part = details.split('Listening:', 1)[1].split('Reading:', 1)[0].strip()

        # Tìm phần 'Reading:'
        if "Reading:" in details:
            reading_part = details.split('Reading:', 1)[1].strip()

    else:
        listening_part = ""
        reading_part = ""

    # Dựng từ điển chứa các phần đã tách
    description_parts = {
        'intro': parts[0].strip() if len(parts) > 0 else "",  # Phần trước 'Bài kiểm tra gồm'
        'listening': listening_part,  # Phần mô tả 'Listening:'
        'reading': reading_part,  # Phần mô tả 'Reading:'
    }

    # Truyền vào context để render vào template
    context = {
        'test': test,
        'description_parts': description_parts,  # Truyền các phần đã tách vào context
    }


    return render(request, 'home_test.html', context)

def test_page(request, test_id):
    test = get_object_or_404(TEST, test_id=test_id)
    questions = QUESTION.objects.filter(test=test)

    if request.method == 'POST':
        total_score = 0
        for question in questions:
            selected_answer = request.POST.get(f'answer_{question.id}')
            if selected_answer == question.correct_answer:
                total_score += 1
        user = request.user
        result = RESULT.objects.create(test=test, user=user, result=total_score)
        return redirect('result_page', result_id=result.id)
    return render(request, 'tests.html', {'test': test, 'questions': questions})
