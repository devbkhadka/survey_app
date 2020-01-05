'''Module for forms of survey app'''

from django import forms
from .models import QuestionTypes, ResponseText

class FormRegistar:
    _instance = None
    def __init__(self):
        if FormRegistar._instance is not None:
            raise Exception('This is singleton class please call static get_instance method')
        
        
        self.register = {}
        FormRegistar._instance = self

    @staticmethod
    def get_instance():
        return FormRegistar._instance if FormRegistar._instance is not None else FormRegistar()

    def register_form(self, question_type, form):
        self.register[question_type] = form

    def get_form_for(self, question_type):
        form = self.register.get(question_type, None)
        if form is not None:
            return form()
        return None


class TextQuestionForm(forms.ModelForm):

    class Meta:
        model = ResponseText
        fields = ['response']
        labels = {
            'response': ''
        }

registar = FormRegistar.get_instance()
registar.register_form(QuestionTypes.TEXT.name, TextQuestionForm)
