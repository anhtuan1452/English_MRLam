from django.shortcuts import render, redirect,get_object_or_404


# Create your views here.
from english.models import TEST, QUESTION
from .forms import TestForm, QuestionForm


def test_list(request):
    tests = TEST.objects.all()  # Get all tests from the database
    return render(request, 'test_list.html', {'tests': tests})


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
        question_forms = [QuestionForm(instance=q) for q in questions]

    # Trả về template với dữ liệu của bài kiểm tra và câu hỏi
    return render(request, 'test_detail.html', {
        'test_form': test_form,
        'question_forms': question_forms,
        'test': test,
    })


def test_add(request):
    if request.method == 'POST':
        # Lấy thông tin từ form
        test_name = request.POST.get('test_name')
        time_limit = request.POST.get('time_limit')

        # Tạo bài kiểm tra mới
        test = TEST.objects.create(test_name=test_name, time=time_limit)

        # Lưu câu hỏi
        for i in range(int(request.POST.get('num_questions'))):
            question_text = request.POST.get(f'question_text_{i}')
            question = QUESTION.objects.create(test=test, question_text=question_text)
            # Thêm các lựa chọn câu hỏi
            for j in range(int(request.POST.get(f'num_choices_{i}'))):
                choice_text = request.POST.get(f'choice_{i}_{j}')
                is_correct = 'correct' in request.POST.getlist(f'correct_{i}')
                # Lưu các lựa chọn
                question.choices.create(choice_text=choice_text, correct=is_correct)

        return redirect('admin_ql_test')  # Redirect về trang danh sách bài kiểm tra

    return render(request, 'test_add.html')


from django.shortcuts import render
from english.models import  RESULT


def test_results_view(request):
    # Get all results with related test and user information
    results = RESULT.objects.select_related('test', 'user').all()

    # Prepare data for the template
    test_results = []
    for index, result in enumerate(results, start=1):
        test_results.append({
            'stt': index,
            'full_name': f"{result.user.last_name} {result.user.first_name}",
            'test_name': result.test.test_name,
            'total_score': f"{result.result}/30",  # Assuming max score is 30
            'test_date': result.test.time,  # You might want to add a date field to Test model
            'duration': "29 phút",  # You might want to add duration field to Result model
        })

    context = {
        'test_results': test_results,
        'page_title': 'Bài kiểm tra',
        'section_title': 'Kết quả',
    }

    return render(request, 'test_results.html', context)