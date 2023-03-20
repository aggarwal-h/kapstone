# Generated by Django 4.1.2 on 2023-03-20 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "misc",
            "0009_imagequote_either provide a quote request or a quote request batch id",
        ),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="imagequote",
            name="Either provide a quote request or a quote request batch id",
        ),
        migrations.AddConstraint(
            model_name="imagequote",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("quote_request__isnull", False),
                        ("quote_request_batch_id__isnull", True),
                    ),
                    models.Q(
                        ("quote_request__isnull", True),
                        ("quote_request_batch_id__isnull", False),
                    ),
                    _connector="OR",
                ),
                name="Either provide a quote request or a quote request batch id",
            ),
        ),
    ]
