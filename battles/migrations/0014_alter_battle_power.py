# Generated by Django 4.2.2 on 2023-06-24 05:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0013_battle_gpt_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='power',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
