'''Test cases for views'''
from unittest.mock import patch, Mock

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.http import QueryDict

from .. import views
from ..models import Survey, Question, QuestionTypes, SurveyResponse, ResponseText
from ..forms import FormRegistar, TextQuestionForm
from .. import forms
from . import factory

class TestSurveysView(TestCase):
    '''Test case for Surveys view'''

    def test_correct_view_called(self):
        '''Test correct view called when "home" url called'''
        called = resolve(reverse("home")).func
        to_be_called = views.surveys

        self.assertTrue(called, to_be_called)

    def test_renders_surveys_template(self):
        '''Test home path renders surveys template'''
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, 'survey/surveys.html')

    def test_sends_surveys_in_context(self):
        '''Test survyes view send all surveys in context'''
        all_surveys = Survey.objects.all()
        response = self.client.get(reverse("home"))
        self.assertQuerysetEqual(response.context["surveys"], all_surveys)


class TestSurveyView(TestCase):
    '''Test case for Survey view'''

    def test_correct_view_called(self):
        '''Test correct view called when "home" url called'''
        called = resolve(reverse("survey:detail", args=[1])).func
        to_be_called = views.survey

        self.assertTrue(called, to_be_called)

    def test_renders_survey_template(self):
        '''Test survey view uses survey template'''
        surveys = factory.create_surveys()
        response = self.client.get(surveys[0].get_absolute_url())
        self.assertTemplateUsed(response, 'survey/survey.html')

    def test_sends_correct_survey_in_context(self):
        '''test correct survey sent in context'''
        survey = factory.create_surveys()[0]
        response = self.client.get(survey.get_absolute_url())
        self.assertEqual(response.context['survey'], survey)

class TestTakeSurveyView(TestCase):
    '''Test case for TakeSurvey view'''

    def setUp(self):
        self.survey = factory.create_survey_with_questions()
        super().setUp()

    def test_correct_view_called(self):
        '''Test correct view called when url invoked'''
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        resolved_function = resolve(takesurvey_url).func
        expected_function = views.take_survey

        self.assertEqual(resolved_function, expected_function)

    def test_renders_correct_template(self):
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        question = Question.objects.filter(survey=self.survey)[0]
        expected_template = f'survey/questions/{question.question_type}.html'
        response = self.client.get(takesurvey_url)
        self.assertTemplateUsed(response, expected_template)

        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, 2])
        question = Question.objects.filter(survey=self.survey)[1]
        expected_template = f'survey/questions/{question.question_type}.html'
        response = self.client.get(takesurvey_url)
        self.assertTemplateUsed(response, expected_template)

    def test_sends_correct_values_in_context(self):
        '''test correct survey sent in context'''
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, 2])
        response = self.client.get(takesurvey_url)
        self.assertEqual(response.context['survey'], self.survey)
        question = Question.objects.filter(survey=self.survey)[1]
        self.assertEqual(response.context['question'], question)
        self.assertEqual(response.context['cur_index'], 2)
        self.assertEqual(response.context['next_url'], views.get_next_question_url(self.survey, 2))

    @patch.object(views, 'get_or_create_survey_response')
    def test_survey_response_id_cookie_set(self, mock_get_or_create_survey_response):
        '''Test survey_response_id cookie is set when take survey url invoked'''
        mock_get_or_create_survey_response.return_value = Mock(pk=15)
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        response = self.client.get(takesurvey_url)
        mock_get_or_create_survey_response.assert_called_once_with(response.wsgi_request, self.survey)
        self.assertEqual(response.cookies.get(f'survey_response_id_{self.survey.pk}').value, '15')
    
    def test_404_status_sent_if_survey_not_exists(self):
        '''Test 404 page is shown if survey does not exist'''
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk+5, 1])
        response = self.client.get(takesurvey_url)
        self.assertEqual(response.status_code, 404)

    def test_404_status_sent_if_question_not_exists(self):
        '''Test 404 page is shown if question does not exist'''
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, self.survey.questions.count()+1])
        response = self.client.get(takesurvey_url)
        self.assertEqual(response.status_code, 404)

    def test_last_question_with_form_redirects_to_finish_on_post(self):
        '''Test last question having form redirects to finish when posted'''
        last_index = self.survey.questions.count()
        form = FormRegistar.get_instance().get_form_class_for(self.survey.questions.last())
        self.assertIsNotNone(form, "Last question of fixture survey must have form")

        survey_response = SurveyResponse.objects.create(survey=self.survey)
        self.client.cookies[f'survey_response_id_{self.survey.pk}'] = survey_response.pk

        with patch.object(views, 'FormRegistar'):
            takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, last_index])
            response = self.client.post(takesurvey_url, data={'dummy_key':'dummy_data'})
            self.assertRedirects(response, reverse('survey:finish_survey', args=[self.survey.pk]))



class TestQuestionTypeSubView(TestCase):
    question_type = None
    def setUp(self):
        self.survey = factory.create_survey_with_questions()
        self.question, self.index = factory.get_question_and_index_of_type(self.survey, self.question_type.name)
        self.url = reverse('survey:take_survey', args=[self.survey.pk, self.index])
        super().setUp()


class TestTextQuestion(TestQuestionTypeSubView):
    question_type = QuestionTypes.TEXT

    def test_sends_correct_form_in_context(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], TextQuestionForm)

    def test_loads_answer_in_form_if_exists(self):
        survey_response = SurveyResponse.objects.create(survey=self.survey)
        ResponseText.objects.create(survey_response=survey_response, question=self.question,
                                    response="This response need to be preloaded")
        
        self.client.cookies[f'survey_response_id_{self.survey.pk}'] = survey_response.pk

        response = self.client.get(self.url)
        self.assertContains(response, "This response need to be preloaded")

    def test_forms_save_method_called_on_post_request(self):
        dummy_data = dict(name='my_name')
        dummy_post = QueryDict('', mutable=True)
        dummy_post.update(dummy_data)
        survey_response = SurveyResponse.objects.create(survey=self.survey)
        # when answer doesn't exists
        self.client.cookies[f'survey_response_id_{self.survey.pk}'] = survey_response.pk
        TextQuestionForm = FormRegistar.get_instance().get_form_class_for(self.question_type.name)
        
        with patch.object(forms, 'TextQuestionForm', side_effect=TextQuestionForm) as MockTextQuestionForm:
            TextQuestionForm.save = Mock()
            self.client.post(self.url, data=dummy_data)
            MockTextQuestionForm.assert_called_once_with(data=dummy_post)
            TextQuestionForm.save.assert_called_once_with()

        # when answer exists
        answer = ResponseText.objects.create(question=self.question, survey_response=survey_response)
        self.client.cookies[f'survey_response_id_{self.survey.pk}'] = survey_response.pk
        TextQuestionForm = FormRegistar.get_instance().get_form_class_for(self.question_type.name)
        
        with patch.object(forms, 'TextQuestionForm', side_effect=TextQuestionForm) as MockTextQuestionForm:
            TextQuestionForm.save = Mock()
            self.client.post(self.url, data=dummy_data)
            MockTextQuestionForm.assert_called_once_with(data=dummy_post, instance=answer)
            TextQuestionForm.save.assert_called_once_with()

    def test_redirects_to_next_question_on_form_post(self):
        response = self.client.post(self.url, data=dict(response="Response from test_views.py"))
        next_url = reverse('survey:take_survey', args=[self.survey.pk, self.index+1])
        self.assertRedirects(response, next_url)

class TestFinishSurveyView(TestCase):
    '''Test case for finish_survey view'''

    def setUp(self):
        self.survey, self.survey_response = factory.create_survey_with_text_question_and_answer()
        self.cookie_key = f'survey_response_id_{self.survey.pk}'
        self.client.cookies[self.cookie_key] = self.survey_response.pk

    def test_renders_correct_template(self):
        response = self.client.get(reverse('survey:finish_survey', args=[self.survey.pk]))
        self.assertTemplateUsed(response, 'survey/questions/finish.html')

    def test_survey_sent_in_context(self):
        '''Test correct survey sent as context'''
        response = self.client.get(reverse('survey:finish_survey', args=[self.survey.pk]))
        self.assertEqual(response.context['survey'], self.survey)

    def test_gives_404_if_no_survey_response(self):
        '''Test gives 404 error if survey_response is invalid or doesn't exists'''
        del self.client.cookies[f'survey_response_id_{self.survey.pk}']
        response = self.client.get(reverse('survey:finish_survey', args=[self.survey.pk]))
        self.assertEqual(response.status_code, 404)

    def test_post_updates_completed_date_of_survey_response(self):
        response = self.client.post(reverse('survey:finish_survey', args=[self.survey.pk]), data={})
        changed_survey_response = SurveyResponse.objects.get(pk=self.survey_response.pk)
        self.assertIsNotNone(changed_survey_response.completed_date)
        self.assertEqual(self.client.cookies.get(self.cookie_key)['max-age'],  0, "cookie for survey_response not cleared")
        self.assertRedirects(response, reverse('survey:thank_you'))
        

class TestThankYouPage(TestCase):
    '''Test case for thank_you view'''

    def test_renders_correct_template(self):
        url = reverse('survey:thank_you')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'survey/thank_you.html')

class TestGetOrCreateSurveyResponse(TestCase):
    '''Test get_or_create_sruvey_response'''

    def test_get_or_create_survey_response(self):
        User = get_user_model()
        user = User.objects.create(username='dev')
        survey = factory.create_survey_with_questions()

        request = Mock()
        request.user = user
        request.COOKIES = {}

        views.get_or_create_survey_response(request, survey)

        survey_response = SurveyResponse.objects.first()
        self.assertEqual(survey_response.survey, survey)
        self.assertEqual(survey_response.user, user)

        request.COOKIES = {f'survey_response_id_{survey.pk}': str(survey_response.pk)}

        self.assertEqual(views.get_or_create_survey_response(request, survey), survey_response)

class TestGetNextQuestionUrl(TestCase):
    '''Test get_next_question_url returns correct url'''
    
    def test_get_next_question_url(self):
        survey = factory.create_survey_with_questions()

        next_url = views.get_next_question_url(survey, 1)
        expected_next_url = reverse('survey:take_survey', args=[survey.pk, 2])
        self.assertEqual(next_url, expected_next_url)

        next_url = views.get_next_question_url(survey, 2)
        expected_next_url = reverse('survey:take_survey', args=[survey.pk, 3])
        self.assertEqual(next_url, expected_next_url)

        next_url = views.get_next_question_url(survey, survey.questions.count())
        expected_next_url = reverse('survey:finish_survey', args=[survey.pk])
        self.assertEqual(next_url, expected_next_url)
