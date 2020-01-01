'''Test cases for views'''

from django.test import TestCase
from django.urls import reverse, resolve


from .. import views
from ..models import Survey
from .factory import create_surveys

RAW_SURVEY = \
{
    'title': 'Your favourite candidate',
    'summary': 'Answer questions like who is your favourite candidate and why',
    'published_date': '2019-4-20 00:00+0545',
}

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
        surveys = create_surveys([RAW_SURVEY])
        response = self.client.get(surveys[0].get_absolute_url())
        self.assertTemplateUsed(response, 'survey/survey.html')

    def test_sends_correct_survey_in_context(self):
        '''test correct survey sent in context'''
        survey = create_surveys([RAW_SURVEY])[0]
        response = self.client.get(survey.get_absolute_url())
        self.assertEqual(response.context['survey'], survey)

class TestTakeSurveyView(TestCase):
    '''Test case for TakeSurvey view'''

    def setUp(self):
        self.survey = create_surveys([RAW_SURVEY])[0]
        self.takesurvey_url = reverse('survey:take_survey', args=[self.survey.pk])
        super().setUp()

    def test_correct_view_called(self):
        
        resolved_function = resolve(self.takesurvey_url).func
        expected_function = views.take_survey

        self.assertEqual(resolved_function, expected_function)

    def test_renders_correct_template(self):
        response = self.client.get(self.takesurvey_url)
        self.assertTemplateUsed(response, 'survey/take_survey.html')

    def test_sends_correct_survey_in_context(self):
        '''test correct survey sent in context'''
        response = self.client.get(self.takesurvey_url)
        self.assertEqual(response.context['survey'], self.survey)