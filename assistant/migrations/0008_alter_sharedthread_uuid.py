# Generated by Django 5.0.7 on 2024-07-14 22:18

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant', '0007_alter_sharedthread_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sharedthread',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
    ]