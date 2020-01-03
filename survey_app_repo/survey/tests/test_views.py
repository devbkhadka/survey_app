'''Test cases for views'''

from django.test import TestCase
from django.urls import reverse, resolve


from .. import views
from ..models import Survey, Question
from .factory import create_surveys, create_survey_with_questions

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
        surveys = create_surveys()
        response = self.client.get(surveys[0].get_absolute_url())
        self.assertTemplateUsed(response, 'survey/survey.html')

    def test_sends_correct_survey_in_context(self):
        '''test correct survey sent in context'''
        survey = create_surveys()[0]
        response = self.client.get(survey.get_absolute_url())
        self.assertEqual(response.context['survey'], survey)

class TestTakeSurveyView(TestCase):
    '''Test case for TakeSurvey view'''

    def setUp(self):
        self.survey = create_survey_with_questions()
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
        print(expected_template)
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

