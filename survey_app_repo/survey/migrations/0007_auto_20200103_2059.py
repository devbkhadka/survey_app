# Generated by Django 2.2.9 on 2020-01-03 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_auto_20200103_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='question_type',
            field=models.CharField(choices=[('DESC', 'Description'), ('TEXT', 'Text')], max_length=255),
        ),
    ]
