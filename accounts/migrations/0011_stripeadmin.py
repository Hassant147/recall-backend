# Generated by Django 5.1.7 on 2025-04-07 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_studentuser_is_approved'),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeAdmin',
            fields=[
            ],
            options={
                'verbose_name': 'Stripe Operations',
                'verbose_name_plural': 'Stripe Operations',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('accounts.transaction',),
        ),
    ]
