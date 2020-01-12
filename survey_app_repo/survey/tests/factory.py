'''Utility function to populate data needed for tests'''
from ..models import Survey, Question, QuestionTypes, SurveyResponse, ResponseText

RAW_SURVEYS = [
    {
        'title': 'Your favourite candidate',
        'summary': 'Answer questions like who is your favourite candidate and why',
        'published_date': '2019-4-20 00:00+0545',
    },
    {
        'title': 'Your view on inflation',
        'summary': 'What do you feel about value of money, do you have some examples?',
        'published_date': '2019-4-20 00:00+0545',
    },
    {
        'title': 'Top movie of 2019',
        'summary': 'Which movie do you like most in the year 2019',
        'published_date': '2019-4-20 00:00+0545',
    }

]

RAW_QUESTIONS = [
    {
        'question': 'Read Description Below',
        'description': 'This is description for qoutation',
        'question_type': QuestionTypes.DESC.name
    },
    {
        'question': 'Please enter your text response',
        'description': 'You can enter free text below',
        'question_type': QuestionTypes.TEXT.name
    },
    {
        'question': 'Check out',
        'description': 'This is description for qoutation',
        'question_type': QuestionTypes.DESC.name
    }
]

def create_surveys():
    '''create dummy surveys for test'''
    surveys = []
    for raw in RAW_SURVEYS:
        surveys.append(Survey.objects.create(**raw))
    return surveys

def create_survey_with_questions():
    '''create survey example with some questions'''
    survey = Survey.objects.create(**RAW_SURVEYS[0])

    for raw in RAW_QUESTIONS:
        question = Question.objects.create(survey=survey, **raw)
        survey.questions.add(question)
    return survey

def create_survey_with_text_question_and_answer():
    '''create survey example with only one question of type text'''
    survey = Survey.objects.create(**RAW_SURVEYS[0])

    for raw in RAW_QUESTIONS:
        if raw['question_type'] == QuestionTypes.TEXT.name:
            question = Question.objects.create(survey=survey, **raw)
            survey.questions.add(question)
            break

    survey_response = SurveyResponse.objects.create(survey=survey)
    ResponseText.objects.create(survey_response=survey_response, question=question)
    return survey, survey_response

def get_question_and_index_of_type(survey, qtype):
    questions = Question.objects.filter(survey=survey)
    for i, question in enumerate(questions):
        if question.question_type == str(qtype):
            return question, i + 1
    return None
