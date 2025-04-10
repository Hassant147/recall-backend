# Generated by Django 5.1.7 on 2025-04-06 06:03

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_subscriptionplan_plan_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='employee_limit',
            field=models.PositiveIntegerField(default='10'),
        ),
        migrations.CreateModel(
            name='UserSearchCount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('count', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='search_counts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'date')},
            },
        ),
    ]
