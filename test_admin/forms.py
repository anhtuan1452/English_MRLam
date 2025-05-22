from django import forms
from english.models import TEST,QUESTION,QUESTION_MEDIA

# Form để lấy bài kiểm tra
class TestForm(forms.ModelForm):
    class Meta:
        model = TEST
        fields = ['test_name', 'test_description', 'duration']
        labels = {
            'test_name': 'Tên bài kiểm tra',
            'test_description': 'Mô tả chi tiết',
            'duration': 'Thời gian làm bài (phút)'
        }
        widgets = {
            'test_name': forms.TextInput(attrs={'class': 'form-control'}),
            'test_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
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
    answer_a = forms.CharField(label='A', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_b = forms.CharField(label='B', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_c = forms.CharField(label='C', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer_d = forms.CharField(label='D', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    correct_answer = forms.ChoiceField(
        label='Đáp án đúng',
        choices=[
            ('', '-- Chọn đáp án đúng --'),
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D')
        ],
        widget=forms.Select(attrs={'class': 'form-select mb-3', 'required': True})
    )

    class Meta:
        model = QUESTION
        fields = ['question_text', 'correct_answer']
        labels = {
            'question_text': 'Câu hỏi',
        }
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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


