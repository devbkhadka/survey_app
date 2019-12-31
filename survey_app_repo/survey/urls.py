'''url patterns for survey app'''
from django.urls import path
from .views import survey


app_name = "survey"
urlpatterns = [
    path("<int:pk>", survey, name="detail"),
]
