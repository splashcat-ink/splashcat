# Generated by Django 5.0.3 on 2024-04-26 22:03

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0022_user_stripe_customer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='coral_friend_url',
            field=models.URLField(blank=True, null=True, validators=[django.core.validators.URLValidator(regex='^https:\\/\\/lounge\\.nintendo\\.com\\/friendcode\\/\\d{4}-\\d{4}-\\d{4}\\/[A-Za-z0-9]{10}$')], verbose_name='Nintendo Switch Online app friend URL'),
        ),
    ]
