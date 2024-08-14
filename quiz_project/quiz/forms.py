from django import forms
from .models import ParentRegistration, Question, Choice, ParentAttempt, Answer
from django.contrib.auth.forms import AuthenticationForm

class ParentRegistrationForm(forms.ModelForm):
    class Meta:
        model = ParentRegistration
        fields = ['parent_name', 'student_name', 'admission_number', 'class_name', 'mobile_number']
        widgets = {
            'class_name': forms.Select(choices=ParentRegistration.CLASS_CHOICES),
        }

class ParentLoginForm(forms.Form):
    admission_number = forms.CharField(
        label="Admission Number",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    mobile_number = forms.CharField(
        label="Mobile Number",
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)
        super(QuizForm, self).__init__(*args, **kwargs)
        if question:
            self.fields[f'question_{question.id}'] = forms.ChoiceField(
                label=question.text,
                choices=[(choice.id, choice.text) for choice in question.choice_set.all()],
                widget=forms.RadioSelect,
                required=False 
            )

class AdminLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

class UploadFileForm(forms.Form):
    file = forms.FileField()