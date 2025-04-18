# Generated by Django 5.1.7 on 2025-04-17 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_rename_timestamp_query_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentuser',
            name='student_id_text',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='student_id',
            field=models.FileField(blank=True, null=True, upload_to='student_ids/'),
        ),
    ]
