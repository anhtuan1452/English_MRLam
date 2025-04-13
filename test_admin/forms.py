from django import forms
from english.models import Test, Question

# Form để lấy bài kiểm tra
class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['test_name', 'test_description', 'time']

# Form để lấy câu hỏi và đáp án
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'answer', 'correct_answer']
