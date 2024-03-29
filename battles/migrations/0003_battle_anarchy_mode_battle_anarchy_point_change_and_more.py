# Generated by Django 4.2.1 on 2023-05-23 14:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0002_player_order_alter_battle_vs_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='anarchy_mode',
            field=models.CharField(blank=True,
                                   choices=[('SERIES', 'Anarchy Battle (Series)'), ('OPEN', 'Anarchy Battle (Open)')],
                                   max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='anarchy_point_change',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='splatfest_clout_multiplier',
            field=models.CharField(blank=True, choices=[('NONE', '1x'), ('DECUPLE', '10x'), ('DRAGON', '100x'),
                                                        ('DOUBLE_DRAGON', '333x')], max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='splatfest_mode',
            field=models.CharField(blank=True,
                                   choices=[('OPEN', 'Splatfest Battle (Open)'), ('PRO', 'Splatfest Battle (Pro)')],
                                   max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='x_battle_rank',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='battle',
            name='x_battle_x_power',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
