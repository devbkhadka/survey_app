'''module for views'''
from django.shortcuts import render, get_object_or_404

from .models import Survey, Question

def surveys(request):
    '''View to show list of all surveys'''
    context = dict(surveys=Survey.objects.all())
    return render(request, 'survey/surveys.html', context=context)


def survey(request, pk):
    '''Detail view for survey'''
    _survey = get_object_or_404(Survey, pk=pk)
    return render(request, 'survey/survey.html', context=dict(survey=_survey))

def take_survey(request, pk, index):
    '''View where user responds to survey'''
    _survey = get_object_or_404(Survey, pk=pk)
    question = Question.objects.filter(survey=_survey)[index-1]
    return render(request, f'survey/questions/{question.question_type}.html',
                   context=dict(survey=_survey, question=question))
