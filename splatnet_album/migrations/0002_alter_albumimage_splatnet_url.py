# Generated by Django 5.0.3 on 2024-04-30 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splatnet_album', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='albumimage',
            name='splatnet_url',
            field=models.URLField(unique=True),
        ),
    ]
