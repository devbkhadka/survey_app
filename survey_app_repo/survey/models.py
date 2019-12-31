'''Models for survey app'''
from django.db import models
from django.urls import reverse

# Create your models here.
class Survey(models.Model):
    '''Model representing a survey'''
    title = models.CharField(max_length=255)
    summary = models.CharField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField()

    def get_absolute_url(self):
        '''returns absolute url of model'''
        return reverse('survey:detail', args=[self.pk])

    def __str__(self):
        return self.title
