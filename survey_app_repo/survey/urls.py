'''url patterns for survey app'''
from django.urls import path
from .views import survey, take_survey, finish_survey, thank_you


app_name = "survey"
urlpatterns = [
    path("<int:pk>", survey, name="detail"),
    path("takesurvey/<int:pk>/<int:index>", take_survey, name="take_survey"),
    path("takesurvey/finish/<int:survey_id>", finish_survey, name="finish_survey"),
    path("thank_you", thank_you, name="thank_you"),
]
