'''Utility function to populate data needed for tests'''
from ..models import Survey

def create_surveys(surveys_raw):
    '''create dummy surveys for test'''
    surveys = []
    for raw in surveys_raw:
        surveys.append(Survey.objects.create(**raw))
    return surveys
