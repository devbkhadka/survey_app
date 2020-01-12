from unittest.mock import Mock, patch

from django.test import TestCase
from .. import forms
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

    def test_register_and_get_form_class_for(self):
        registar = FormRegistar.get_instance()

        mock1 = Mock()
        mock2 = Mock()

        registar.register_form('key1', mock1)
        registar.register_form('key2', mock2)

        registar = FormRegistar.get_instance()
        self.assertEqual(registar.get_form_class_for('key2'), mock2)
        self.assertEqual(registar.get_form_class_for('key1'), mock1)

        self.assertEqual(registar.get_form_class_for('key3'), forms.BaseQuestionForm)
        


class TestTextQuestionForm(TestCase):
    '''Test case for TextQuestionForm'''

    def setUp(self):
        self.survey = create_survey_with_questions()
        self.question, _ = get_question_and_index_of_type(self.survey, QuestionTypes.TEXT.name)
        self.survey_response = SurveyResponse.objects.create(survey=self.survey)
        super().setUp()

    @patch.object(forms, 'TextQuestionForm')
    def test_get_form_instance(self, MockTextQuestionForm):
        '''Test load_instance method'''
        
        # survey_reponse don't have answer yet
        form = TextQuestionForm.get_form_instance(self.question, self.survey_response)
        MockTextQuestionForm.assert_called_once_with()
        self.assertEqual(MockTextQuestionForm.return_value, form)
        
        # survey_reponse don't have answer yet and form arguments are sent
        MockTextQuestionForm.reset_mock()
        form = TextQuestionForm.get_form_instance(self.question, self.survey_response, arg1='abc', arg2=33)
        MockTextQuestionForm.assert_called_once_with(arg1='abc', arg2=33)
        self.assertEqual(MockTextQuestionForm.return_value, form)
        
        # survey_response has answer for the question
        answer = ResponseText.objects.create(question=self.question, survey_response=self.survey_response)
        MockTextQuestionForm.reset_mock()
        form = TextQuestionForm.get_form_instance(self.question, self.survey_response)
        MockTextQuestionForm.assert_called_once_with(instance=answer)
        self.assertEqual(MockTextQuestionForm.return_value, form)

        # survey_response has answer for the question and form arguments are sent
        MockTextQuestionForm.reset_mock()
        form = TextQuestionForm.get_form_instance(self.question, self.survey_response, arg1='abc', arg2=33)
        MockTextQuestionForm.assert_called_once_with(instance=answer, arg1='abc', arg2=33)
        self.assertEqual(MockTextQuestionForm.return_value, form)

    def test_save_can_create_answer(self):
        form = TextQuestionForm.get_form_instance(self.question, self.survey_response,
                                                  data={'response': 'This is answer from test_form'})
        form.save()

        answer = ResponseText.objects.first()
        self.assertEqual(answer.response, 'This is answer from test_form')
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.survey_response, self.survey_response)

    def test_save_can_change_anser(self):
        ResponseText.objects.create(response='This is answer from test_form',
                                    question=self.question, survey_response=self.survey_response)
        
        form = TextQuestionForm.get_form_instance(self.question, self.survey_response,
                                                  data={'response': 'This is answer from test_form changed'})
        form.save()

        answer = ResponseText.objects.first()
        self.assertEqual(answer.response, 'This is answer from test_form changed')
        self.assertEqual(answer.question, self.question)
        self.assertEqual(answer.survey_response, self.survey_response)

