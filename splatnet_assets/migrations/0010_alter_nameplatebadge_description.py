# Generated by Django 5.0.2 on 2024-03-30 07:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splatnet_assets', '0009_merge_20240302_0704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nameplatebadge',
            name='description',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='splatnet_assets.localizationstring'),
        ),
    ]
