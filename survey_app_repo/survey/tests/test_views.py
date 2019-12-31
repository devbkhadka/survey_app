'''Test cases for views'''

from django.test import TestCase
from django.urls import reverse, resolve


from .. import views
from ..models import Survey
from .factory import create_surveys

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
        surveys = create_surveys(["survey 1"])
        response = self.client.get(surveys[0].get_absolute_url())
        self.assertTemplateUsed(response, 'survey/survey.html')

    def test_sends_correct_survey_in_context(self):
        '''test correct survey sent in context'''
        survey = create_surveys(["survey 1"])[0]
        response = self.client.get(survey.get_absolute_url())
        self.assertEqual(response.context['survey'], survey)
