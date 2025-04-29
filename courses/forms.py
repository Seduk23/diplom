from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Course, Lesson

class StudentSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
        return user

class TeacherSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user
    
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class TestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        questions = kwargs.pop('questions')
        super().__init__(*args, **kwargs)
        
        for question in questions:
            if question.question_type == 'text':
                self.fields[f'question_{question.id}'] = forms.CharField(
                    label=question.text,
                    widget=forms.Textarea(attrs={'rows': 3}))  # Закрывающая скобка добавлена
            else:
                choices = [(a.id, a.text) for a in question.answers.all()]
                if question.question_type == 'single':
                    self.fields[f'question_{question.id}'] = forms.ChoiceField(
                        label=question.text,
                        choices=choices,
                        widget=forms.RadioSelect)
                else:
                    self.fields[f'question_{question.id}'] = forms.MultipleChoiceField(
                        label=question.text,
                        choices=choices,
                        widget=forms.CheckboxSelectMultiple)

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'order', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
        }

