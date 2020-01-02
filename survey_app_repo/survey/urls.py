'''url patterns for survey app'''
from django.urls import path
from .views import survey, take_survey


app_name = "survey"
urlpatterns = [
    path("<int:pk>", survey, name="detail"),
    path("takesurvey/<int:pk>/<int:index>", take_survey, name="take_survey"),
]
