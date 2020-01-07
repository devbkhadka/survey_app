'''Test cases for views'''
from unittest.mock import patch, Mock

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from .. import views
from ..models import Survey, Question, QuestionTypes, SurveyResponse, ResponseText
from ..forms import TextQuestionForm
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
        self.assertEqual(response.context['questions_count'], self.survey.questions.count())

    @patch.object(views, 'get_or_create_survey_response')
    def test_survey_response_id_cookie_set(self, mock_get_or_create_survey_response):
        '''Test survey_response_id cookie is set when take survey url invoked'''
        mock_get_or_create_survey_response.return_value = Mock(pk=15)
        takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        response = self.client.get(takesurvey_url)
        mock_get_or_create_survey_response.assert_called_once_with(response.wsgi_request, self.survey)
        self.assertEqual(response.cookies.get(f'survey_response_id_{self.survey.pk}').value, '15')

class TestQuestionTypeSubView(TestCase):
    question_type = None
    def setUp(self):
        self.survey = factory.create_survey_with_questions()
        index, self.question = factory.get_question_and_index_of_type(self.survey, self.question_type.name)
        self.url = reverse('survey:take_survey', args=[self.survey.pk, index])
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
