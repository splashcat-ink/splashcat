# Generated by Django 4.2.1 on 2023-05-04 23:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0008_alter_githublink_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='display_name',
            field=models.CharField(blank=True, max_length=30, verbose_name='display name'),
        ),
    ]
