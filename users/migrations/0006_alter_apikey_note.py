# Generated by Django 4.2 on 2023-04-13 05:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0005_apikey_note_alter_apikey_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='note',
            field=models.TextField(blank=True, null=True),
        ),
    ]
