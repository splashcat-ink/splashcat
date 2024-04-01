# Generated by Django 5.0.2 on 2024-02-28 22:10

import battles.models
import django_choices_field.fields
import splatnet_assets.common_model_choices
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0021_battlegroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='anarchy_mode',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('SERIES', 'Anarchy Battle (Series)'), ('OPEN', 'Anarchy Battle (Open)')], choices_enum=battles.models.Battle.AnarchyMode, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='judgement',
            field=django_choices_field.fields.TextChoicesField(choices=[('WIN', 'Victory'), ('LOSE', 'Defeat'), ('DRAW', 'Draw'), ('EXEMPTED_LOSE', 'Defeat (Exempted)'), ('DEEMED_LOSE', 'Deemed Lose')], choices_enum=battles.models.Battle.BattleJudgement, db_index=True, max_length=13),
        ),
        migrations.AlterField(
            model_name='battle',
            name='knockout',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('NEITHER', 'Neither'), ('WIN', 'Victory'), ('LOSE', 'Defeat')], choices_enum=battles.models.KnockoutJudgement, max_length=7, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='splatfest_clout_multiplier',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('NONE', '1x'), ('DECUPLE', '10x'), ('DRAGON', '100x'), ('DOUBLE_DRAGON', '333x')], choices_enum=battles.models.Battle.SplatfestBattleCloutMultiplier, max_length=13, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='splatfest_mode',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('OPEN', 'Splatfest Battle (Open)'), ('PRO', 'Splatfest Battle (Pro)')], choices_enum=battles.models.Battle.SplatfestBattleType, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='battle',
            name='vs_mode',
            field=django_choices_field.fields.TextChoicesField(choices=[('REGULAR', 'Regular Battle'), ('CHALLENGE', 'Challenge'), ('FEST', 'Splatfest Battle'), ('BANKARA', 'Anarchy Battle'), ('X_MATCH', 'X Battle'), ('PRIVATE', 'Private Battle')], choices_enum=battles.models.Battle.VsMode, max_length=9),
        ),
        migrations.AlterField(
            model_name='battle',
            name='vs_rule',
            field=django_choices_field.fields.TextChoicesField(choices=[('TURF_WAR', 'Turf War'), ('TRI_COLOR', 'Tricolor Turf War'), ('AREA', 'Splat Zones'), ('LOFT', 'Tower Control'), ('CLAM', 'Clam Blitz'), ('GOAL', 'Rainmaker')], choices_enum=battles.models.Battle.VsRule, max_length=9),
        ),
        migrations.AlterField(
            model_name='battle',
            name='x_battle_division',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('UNSPECIFIED', 'Unspecified'), ('TENTATEK', 'Tentatek'), ('TAKOROKA', 'Takoroka')], choices_enum=splatnet_assets.common_model_choices.XBattleDivisions, max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='species',
            field=django_choices_field.fields.TextChoicesField(choices=[('INKLING', 'Inkling'), ('OCTOLING', 'Octoling')], choices_enum=battles.models.Player.Species, max_length=8),
        ),
        migrations.AlterField(
            model_name='team',
            name='judgement',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('WIN', 'Victory'), ('LOSE', 'Defeat'), ('DRAW', 'Draw')], choices_enum=battles.models.Judgement, max_length=4, null=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='tricolor_role',
            field=django_choices_field.fields.TextChoicesField(blank=True, choices=[('ATTACK1', 'Attack 1'), ('ATTACK2', 'Attack 2'), ('DEFENSE', 'Defense')], choices_enum=battles.models.Team.TricolorRole, max_length=7, null=True),
        ),
    ]
