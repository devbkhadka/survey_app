# Generated by Django 2.2.9 on 2020-01-02 06:18

from django.db import migrations, models
import survey_app_repo.survey.models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_question'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[(survey_app_repo.survey.models.QuestionTypes('Description'), 'Description'), (survey_app_repo.survey.models.QuestionTypes('Text'), 'Text')], max_length=255),
        ),
    ]
