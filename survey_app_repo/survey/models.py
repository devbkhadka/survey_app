'''Models for survey app'''
from enum import Enum

from django.db import models
from django.urls import reverse

from django.conf import settings

# Create your models here.
class Survey(models.Model):
    '''Model representing a survey'''
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=400, default='', blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        '''returns absolute url of model'''
        return reverse('survey:detail', args=[self.pk])

    def __str__(self):
        return self.title


class QuestionTypes(Enum):
    DESC = 'Description'
    TEXT = 'Text'

class Question(models.Model):
    question = models.CharField(max_length=255)
    description = models.CharField(max_length=400)
    question_type = models.CharField(max_length=255, choices=[(tag.name, tag.value) for tag in QuestionTypes])
    survey = models.ForeignKey(Survey, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return self.question

class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)


class ResponseText(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE)
    response = models.CharField(max_length=400, null=True, blank=True)

    class Meta:
        unique_together = ['question', 'survey_response']

    