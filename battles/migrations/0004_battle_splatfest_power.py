# Generated by Django 4.2.1 on 2023-05-23 14:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0003_battle_anarchy_mode_battle_anarchy_point_change_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='splatfest_power',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
