# Generated by Django 5.0.3 on 2024-05-11 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0028_alter_battle_splatnet_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='statink_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='statink_username',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
