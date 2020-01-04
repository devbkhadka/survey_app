'''module for views'''
from django.shortcuts import render, get_object_or_404

from .models import Survey, Question
from .forms import FormRegistar

form_registar = FormRegistar.get_instance()
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
    questions = Question.objects.filter(survey=_survey)
    question = questions[index-1]
    count = questions.count()
    question_form = form_registar.get_form_for(question.question_type)
    return render(request, f'survey/questions/{question.question_type}.html',
                  context=dict(survey=_survey, question=question, cur_index=index,
                               questions_count=count, form=question_form))

