# Generated by Django 5.0.6 on 2024-06-16 05:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_user_profile_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='page_background',
            field=models.ImageField(blank=True, null=True, upload_to='page_backgrounds', verbose_name='page background'),
        ),
    ]
