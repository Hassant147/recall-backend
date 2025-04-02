# Generated by Django 5.1.7 on 2025-03-28 23:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_query_main_sources_query_corrected_query'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='is_popular',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='stripe_price_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='company',
            name='employee_limit',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True)),
                ('stripe_subscription_id', models.CharField(blank=True, max_length=100, null=True)),
                ('plan_id', models.CharField(max_length=50)),
                ('status', models.CharField(default='inactive', max_length=50)),
                ('current_period_start', models.DateTimeField(blank=True, null=True)),
                ('current_period_end', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stripe_subscription', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stripe_invoice_id', models.CharField(max_length=100)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=100, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=255)),
                ('receipt_url', models.URLField(blank=True, null=True)),
                ('date', models.DateTimeField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
