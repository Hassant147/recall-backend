# Generated by Django 5.1.7 on 2025-03-28 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_merge_20240328_0000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='query',
            name='main_sources',
        ),
        migrations.AddField(
            model_name='query',
            name='corrected_query',
            field=models.TextField(blank=True, null=True),
        ),
    ]
