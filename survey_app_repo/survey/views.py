'''module for views'''
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import Http404
from django.utils import timezone

from .models import Survey, Question, SurveyResponse
from .forms import FormRegistar

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
    survey_response = get_or_create_survey_response(request, _survey)

    questions = Question.objects.filter(survey=_survey)
    if index < 1 or index > questions.count():
        raise Http404("Question doesn't exists")

    question = questions[index-1]
    count = questions.count()
    form_registar = FormRegistar.get_instance()
    FormClass = form_registar.get_form_class_for(question.question_type)

    if request.method == "POST":
        question_form = FormClass.get_form_instance(question, survey_response, data=request.POST)
        question_form.save()
        return redirect(get_next_question_url(_survey, index))

    question_form = FormClass.get_form_instance(question, survey_response)

    response = render(request, f'survey/questions/{question.question_type}.html',
                      context=dict(survey=_survey, question=question, cur_index=index,
                                   next_url=get_next_question_url(_survey, index) ,form=question_form))

    response.set_cookie(f'survey_response_id_{_survey.pk}', survey_response.pk)
    return response

def finish_survey(request, survey_id):
    _survey = get_object_or_404(Survey, pk=survey_id)
    response_id = request.COOKIES.get(f'survey_response_id_{_survey.pk}')
    survey_response = get_object_or_404(SurveyResponse, pk=response_id)

    if request.method == "POST":
        survey_response.completed_date = timezone.now()
        survey_response.save()
        response = redirect(reverse('survey:thank_you'))
        response.delete_cookie(f'survey_response_id_{_survey.pk}')
        return response

    return render(request, 'survey/questions/finish.html', context=dict(survey=_survey))

def thank_you(request):
    return render(request, 'survey/thank_you.html')

def get_next_question_url(_survey, cur_index):
    index = cur_index + 1
    if index > _survey.questions.count():
        return reverse('survey:finish_survey', args=[_survey.pk])

    return reverse('survey:take_survey', args=[_survey.pk, index])    

def get_or_create_survey_response(request, _survey):
    response_id = request.COOKIES.get(f'survey_response_id_{_survey.pk}')
    response_id = int(response_id) if response_id is not None else None
    user = request.user if request.user.is_authenticated else None

    response_query = SurveyResponse.objects.filter(pk=response_id)

    if response_query.count() > 0:
        return response_query.first()

    return SurveyResponse.objects.create(survey=_survey, user=user)
