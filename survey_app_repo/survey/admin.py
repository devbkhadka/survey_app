from django.contrib import admin
from .models import Survey, Question

admin.site.site_header = 'Survey App Admin'


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0


class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_date', 'published']
    list_filter = ['created_date', 'published']

    inlines = [QuestionInline]


admin.site.register(Survey, SurveyAdmin)

admin.site.register(Question)
