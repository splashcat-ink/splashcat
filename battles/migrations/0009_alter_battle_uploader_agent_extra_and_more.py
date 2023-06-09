# Generated by Django 4.2.1 on 2023-06-09 08:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0008_battle_uploader_agent_extra_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='uploader_agent_extra',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='uploader_agent_name',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='uploader_agent_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]