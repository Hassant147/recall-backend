# Generated by Django 5.1.7 on 2025-04-06 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_studentuser_customuser_is_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentuser',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
