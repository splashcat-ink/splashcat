# Generated by Django 4.2 on 2023-04-29 23:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('battles', '0003_player_species'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='judgement',
            field=models.CharField(choices=[('WIN', 'Victory'), ('LOSE', 'Defeat'), ('DRAW', 'Draw'),
                                            ('EXEMPTED_LOSE', 'Defeat (Exempted)'), ('DEEMED_LOSE', 'Deemed Lose')],
                                   max_length=32),
        ),
        migrations.AlterField(
            model_name='battle',
            name='knockout',
            field=models.CharField(blank=True, choices=[('NEITHER', 'Neither'), ('WIN', 'Victory'), ('LOSE', 'Defeat')],
                                   max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='vs_mode',
            field=models.CharField(
                choices=[('REGULAR', 'Regular Battle'), ('LEAGUE', 'League Battle'), ('FEST', 'Splatfest Battle'),
                         ('BANKARA', 'Anarchy Battle'), ('X_MATCH', 'X Battle')], max_length=32),
        ),
        migrations.AlterField(
            model_name='team',
            name='judgement',
            field=models.CharField(choices=[('WIN', 'Victory'), ('LOSE', 'Defeat'), ('DRAW', 'Draw')], max_length=32),
        ),
        migrations.AddIndex(
            model_name='battle',
            index=models.Index(fields=['uploader', '-played_time'], name='battles_bat_uploade_f09b98_idx'),
        ),
    ]