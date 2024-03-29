# Generated by Django 4.2.2 on 2023-07-16 08:42

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='privacy_level',
            field=models.CharField(choices=[('PUBLIC', 'Public'), ('RESTRICTED', 'Restricted'), ('PRIVATE', 'Private')],
                                   default='PUBLIC', max_length=20),
        ),
        migrations.AlterField(
            model_name='group',
            name='pending_invites',
            field=models.ManyToManyField(blank=True, null=True, related_name='pending_group_invites',
                                         to=settings.AUTH_USER_MODEL),
        ),
    ]
