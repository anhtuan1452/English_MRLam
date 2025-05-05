from django import forms
from english.models import TEST,QUESTION,QUESTION_MEDIA

# Form để lấy bài kiểm tra
class TestForm(forms.ModelForm):
    class Meta:
        model = TEST
        fields = ['test_name', 'test_description', 'duration']
        widgets = {
            'test_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên bài kiểm tra'}),
            'test_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Mô tả bài kiểm tra'}),
            'duration': forms.TimeInput(
                format='%H:%M',
                attrs={'class': 'form-control', 'placeholder': 'HH:MM'}
            ),
        }

# Form để lấy câu hỏi và đáp án
class QuestionForm(forms.ModelForm):
    class Meta:
        model = QUESTION
        fields = ['question_text', 'answer', 'correct_answer']

class CustomQuestionForm(forms.ModelForm):
    answer_a = forms.CharField(
        label='Đáp án A',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập đáp án A'})
    )
    answer_b = forms.CharField(
        label='Đáp án B',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập đáp án B'})
    )
    answer_c = forms.CharField(
        label='Đáp án C',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập đáp án C'})
    )

    answer_d = forms.CharField(
        label='Đáp án D',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập đáp án D'})
    )
    # media_audio_file = forms.CharField(label='Link Audio (nếu có)', required=False, widget=forms.TextInput(
    #     attrs={'class': 'form-control', 'placeholder': 'Dán link audio'}))
    # media_paragraph = forms.CharField(label='Đoạn văn (nếu có)', required=False, widget=forms.Textarea(
    #     attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Nhập đoạn văn'}))
    link_audio = forms.CharField(
        label='Link Audio (nếu có):',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    paragraph = forms.CharField(
        label='Đoạn văn (nếu có):',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )
    class Meta:
        model = QUESTION
        fields = ['question_text', 'correct_answer','question_media']
        labels = {
            'question_text': 'Câu hỏi',
            'correct_answer': 'Đáp án đúng (A/B/C/D)',
            'question_media': 'Media'
        }
        widgets = {
            'question_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Nhập nội dung câu hỏi'}),
            'correct_answer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: A'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['question_media'].required = False
        self.fields['question_media'].widget = forms.HiddenInput()
        if self.instance and self.instance.answer:
            answers = self.instance.answer.split(';')
            self.fields['answer_a'].initial = answers[0] if len(answers) > 0 else ''
            self.fields['answer_b'].initial = answers[1] if len(answers) > 1 else ''
            self.fields['answer_c'].initial = answers[2] if len(answers) > 2 else ''
            self.fields['answer_d'].initial = answers[3] if len(answers) > 3 else ''

    def clean(self):
        cleaned_data = super().clean()
        a = cleaned_data.get('answer_a', '')
        b = cleaned_data.get('answer_b', '')
        c = cleaned_data.get('answer_c', '')
        d = cleaned_data.get('answer_d', '')
        self.instance.answer = ';'.join([a, b, c, d])
        return cleaned_data

class QuestionMediaForm(forms.ModelForm):
    class Meta:
        model = QUESTION_MEDIA
        fields = ['audio_file', 'paragraph']
        labels = {
            'audio_file': 'Link Audio (Google Drive)',
            'paragraph': 'Đoạn văn',
        }
        widgets = {
            'audio_file': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Link Google Drive'}),
            'paragraph': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Đoạn văn đi kèm'}),
        }