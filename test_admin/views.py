from django.shortcuts import render

# Create your views here.
from english.models import Test

def test_list(request):
    tests = Test.objects.all()  # Get all tests from the database
    return render(request, 'test_list.html', {'tests': tests})


def test_add(request):
    if request.method == 'POST':
        # Lấy thông tin từ form
        test_name = request.POST.get('test_name')
        time_limit = request.POST.get('time_limit')

        # Tạo bài kiểm tra mới
        test = Test.objects.create(test_name=test_name, time=time_limit)

        # Lưu câu hỏi
        for i in range(int(request.POST.get('num_questions'))):
            question_text = request.POST.get(f'question_text_{i}')
            question = Question.objects.create(test=test, question_text=question_text)
            # Thêm các lựa chọn câu hỏi
            for j in range(int(request.POST.get(f'num_choices_{i}'))):
                choice_text = request.POST.get(f'choice_{i}_{j}')
                is_correct = 'correct' in request.POST.getlist(f'correct_{i}')
                # Lưu các lựa chọn
                question.choices.create(choice_text=choice_text, correct=is_correct)

        return redirect('admin_ql_test')  # Redirect về trang danh sách bài kiểm tra

    return render(request, 'test_add.html')


from django.shortcuts import render
from english.models import Test, Result, UserProfile


def test_results_view(request):
    # Get all results with related test and user information
    results = Result.objects.select_related('test', 'user').all()

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