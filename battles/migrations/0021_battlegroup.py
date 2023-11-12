# Generated by Django 4.2.4 on 2023-11-12 01:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('battles', '0020_alter_player_name_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='BattleGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('battles', models.ManyToManyField(to='battles.battle')),
                (
                    'creator',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]