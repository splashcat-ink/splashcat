# Generated by Django 4.2.2 on 2023-06-28 03:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0014_alter_battle_power'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='battle',
            name='battles_bat_uploade_7668dd_idx',
        ),
        migrations.AddIndex(
            model_name='battle',
            index=models.Index(fields=['-uploaded_at'], name='battles_bat_uploade_6eb754_idx'),
        ),
    ]
