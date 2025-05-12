from django import forms
from english.models import TEST,QUESTION,QUESTION_MEDIA

# Form để lấy bài kiểm tra
class TestForm(forms.ModelForm):
    class Meta:
        model = TEST
        fields = ['test_name', 'test_description', 'duration']
        widgets = {
            'test_name': forms.TextInput(attrs={'class': 'form-control'}),
            'test_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'duration': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class QuestionMediaForm(forms.ModelForm):
    class Meta:
        model = QUESTION_MEDIA
        fields = ['audio_file', 'paragraph']
        labels = {
            'audio_file': 'File Audio (nếu có)',
            'paragraph': 'Đoạn văn (nếu có)',
        }
        widgets = {
            'audio_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'paragraph': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# Form để lấy câu hỏi và đáp án
class QuestionForm(forms.ModelForm):
    class Meta:
        model = QUESTION
        fields = ['question_text', 'answer', 'correct_answer']


class CustomQuestionForm(forms.ModelForm):
    answer_a = forms.CharField(label='Đáp án A', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_b = forms.CharField(label='Đáp án B', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_c = forms.CharField(label='Đáp án C', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_d = forms.CharField(label='Đáp án D', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = QUESTION
        fields = ['question_text', 'correct_answer']
        labels = {
            'question_text': 'Câu hỏi',
            'correct_answer': 'Đáp án đúng (A/B/C/D)',
        }
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        answer = self.instance.answer or {}
        self.fields['answer_a'].initial = answer.get('A', '')
        self.fields['answer_b'].initial = answer.get('B', '')
        self.fields['answer_c'].initial = answer.get('C', '')
        self.fields['answer_d'].initial = answer.get('D', '')

    def clean(self):
        cleaned_data = super().clean()
        self.instance.answer = {
            'A': cleaned_data.get('answer_a', ''),
            'B': cleaned_data.get('answer_b', ''),
            'C': cleaned_data.get('answer_c', ''),
            'D': cleaned_data.get('answer_d', ''),
        }
        return cleaned_data


