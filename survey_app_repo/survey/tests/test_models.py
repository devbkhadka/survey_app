'''Test cases for models'''
from datetime import timedelta, datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction



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

class TestSurveyResponseModel(TestCase):
    '''Test case for SurveyResponse model'''

    def setUp(self):
        self.survey = create_survey_with_questions()

    def test_can_create_survey_response(self):
        User = get_user_model()
        user = User.objects.create(username='test')
        models.SurveyResponse.objects.create(survey=self.survey, user=user)
        self.assertEqual(models.SurveyResponse.objects.count(), 1)
        # create with user null
        models.SurveyResponse.objects.create(survey=self.survey)
        self.assertEqual(models.SurveyResponse.objects.count(), 2)


class TestResponseText(TestCase):
    '''Test model ResponseText'''

    def setUp(self):
        self.survey = create_survey_with_questions()
        self.question = self.survey.questions.first()

    def test_can_create_response_text(self):
        survey_response = models.SurveyResponse.objects.create(survey=self.survey)
        models.ResponseText.objects.create(survey_response=survey_response, question=self.question, 
                                            response='This is my response')


        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                models.ResponseText.objects.create(survey_response=survey_response, question=self.question,
                                                    response='This is my response2')

        survey_response2 = models.SurveyResponse.objects.create(survey=self.survey)

        models.ResponseText.objects.create(survey_response=survey_response2, question=self.question,
                                           response='This is my response2')

        self.assertEqual(models.SurveyResponse.objects.count(), 2)
