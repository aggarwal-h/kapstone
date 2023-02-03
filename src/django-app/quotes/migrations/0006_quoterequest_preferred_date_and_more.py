# Generated by Django 4.1.2 on 2023-02-02 02:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quotes", "0005_remove_quoterequest_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="quoterequest",
            name="preferred_date",
            field=models.DateField(
                blank=True,
                default=datetime.datetime(
                    2023, 2, 2, 2, 6, 49, 900953, tzinfo=datetime.timezone.utc
                ),
                verbose_name="preferred date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="quoterequest",
            name="preferred_time",
            field=models.TimeField(
                blank=True,
                default=datetime.datetime(
                    2023, 2, 2, 2, 6, 54, 95474, tzinfo=datetime.timezone.utc
                ),
                verbose_name="preferred time",
            ),
            preserve_default=False,
        ),
    ]
