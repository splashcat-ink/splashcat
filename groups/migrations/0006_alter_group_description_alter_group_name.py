# Generated by Django 5.1.1 on 2024-09-30 00:36

import groups.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0005_alter_group_pending_invites_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(blank=True, default='', validators=[groups.models.validate_no_profanity]),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=255, validators=[groups.models.validate_no_profanity]),
        ),
    ]
