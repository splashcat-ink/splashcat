# Generated by Django 4.2.3 on 2023-07-22 20:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0019_battle_battles_bat_played__a334b4_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='name_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]