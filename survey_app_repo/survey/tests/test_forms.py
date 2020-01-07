from django.test import TestCase
from ..forms import FormRegistar, TextQuestionForm
from .factory import create_survey_with_questions, get_question_and_index_of_type
from ..models import SurveyResponse, ResponseText, QuestionTypes

class TestFormRegistar(TestCase):

    def test_get_instance(self):
        registar = FormRegistar.get_instance()
        self.assertIsInstance(registar, FormRegistar)
        registar2 = FormRegistar.get_instance()
        self.assertTrue(registar is registar2)

    def test_constructor_raises_error_when_called_directly(self):
        FormRegistar.get_instance()
        with self.assertRaises(Exception):
            FormRegistar()

    def test_register_and_get_form(self):
        registar = FormRegistar.get_instance()

        registar.register_form('key1', TestCase)
        registar.register_form('key2', Exception)

        registar = FormRegistar.get_instance()
        self.assertIsInstance(registar.get_form_for('key2'), Exception)
        self.assertIsInstance(registar.get_form_for('key1'), TestCase)


class TestTextQuestionForm(TestCase):
    '''Test case for TextQuestionForm'''

    def test_load_instance(self):
        '''Test load_instance method'''
        survey = create_survey_with_questions()
        _, question = get_question_and_index_of_type(survey, QuestionTypes.TEXT.name)
        survey_response = SurveyResponse.objects.create(survey=survey)
        answer = ResponseText.objects.create(question=question, survey_response=survey_response)
        
        form = TextQuestionForm()
        form.load_instance(question=question, survey_response=survey_response)

        self.assertEqual(form.instance, answer)
