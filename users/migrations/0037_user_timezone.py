# Generated by Django 5.1.1 on 2024-10-02 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_alter_user_bio_alter_user_display_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='timezone',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='timezone'),
        ),
    ]