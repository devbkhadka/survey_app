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


    def get_form_class_for(self, question_type):
        return self.register.get(question_type, BaseQuestionForm)


class BaseQuestionForm(forms.Form):


    @staticmethod
    def get_form_instance(question, survey_response, **kwargs):
        return None


class TextQuestionForm(forms.ModelForm):

    class Meta:
        model = ResponseText
        fields = ['response']
        labels = {
            'response': ''
        }

    @staticmethod
    def get_form_instance(question, survey_response, **kwargs):
        '''Load response from database if exists'''
        answer = ResponseText.objects.filter(survey_response=survey_response, question=question).first()
        if answer is not None:
            form = TextQuestionForm(instance=answer, **kwargs)
        else:
            form = TextQuestionForm(**kwargs)
        
        form.instance.question = question
        form.instance.survey_response = survey_response
        return form


# register forms to question types
registar = FormRegistar.get_instance()
registar.register_form(QuestionTypes.TEXT.name, TextQuestionForm)
