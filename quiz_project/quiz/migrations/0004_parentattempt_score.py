# Generated by Django 5.1 on 2024-08-13 17:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_alter_parentregistration_mobile_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentattempt',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
