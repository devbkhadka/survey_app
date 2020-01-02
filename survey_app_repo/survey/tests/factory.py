'''Utility function to populate data needed for tests'''
from ..models import Survey, Question, QuestionTypes

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
        'question_type': QuestionTypes.DESC
    },
    {
        'question': 'Read Description Below',
        'description': 'This is description for qoutation',
        'question_type': QuestionTypes.TEXT
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
