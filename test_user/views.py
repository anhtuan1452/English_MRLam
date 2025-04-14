from django.shortcuts import render, redirect, get_object_or_404

from english.models import TEST, QUESTION, RESULT

# Create your views here.
def home_test(request):
    return render(request, 'home_test.html')

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
