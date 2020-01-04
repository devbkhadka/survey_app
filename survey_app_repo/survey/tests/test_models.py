'''Test cases for models'''
from datetime import timedelta, datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone



from .. import models
from .factory import create_survey_with_questions

RAW_SURVEY = \
{
    'title': 'Your favourite candidate',
    'summary': 'Answer questions like who is your favourite candidate and why',
    'published_date': '2019-4-20 00:00+0545',
}

class TestSurveyModel(TestCase):
    '''Test case for Survey Model'''

    def setUp(self):
        self.survey = models.Survey.objects.create(**RAW_SURVEY)

    def test_can_create_survey(self):
        '''Test can create survey with given information'''
        surveys = models.Survey.objects.all()
        self.assertEqual(surveys.count(), 1)
        self.assertEqual(surveys[0].title, RAW_SURVEY['title'])
        self.assertEqual(surveys[0].summary, RAW_SURVEY['summary'])
        pdate = datetime.strptime(RAW_SURVEY['published_date'], '%Y-%m-%d %H:%M%z')
        self.assertEqual(surveys[0].published_date, pdate)
        self.assertFalse(surveys[0].published)
        self.assertTrue((timezone.now()-surveys[0].created_date) < timedelta(seconds=5))

    def test_gives_correct_absolute_url(self):
        '''Test absolute url implemented and give correct url'''
        expected_url = reverse('survey:detail', args=[self.survey.pk])
        self.assertEqual(self.survey.get_absolute_url(), expected_url)

class TestQuestionModel(TestCase):
    '''Test case for question model'''

    def setUp(self):
        self.survey = create_survey_with_questions()

    def test_can_create_question_for_survey(self):
        survey = models.Survey.objects.get(pk=self.survey.pk) # raises if survey not found
        self.assertEqual(survey.questions.count(), 3)
