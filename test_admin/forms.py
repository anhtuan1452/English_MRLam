from django import forms
from english.models import TEST,QUESTION

# Form để lấy bài kiểm tra
class TestForm(forms.ModelForm):
    class Meta:
        model = TEST
        fields = ['test_name', 'test_description']

# Form để lấy câu hỏi và đáp án
class QuestionForm(forms.ModelForm):
    class Meta:
        model = QUESTION
        fields = ['question_text', 'answer', 'correct_answer']
