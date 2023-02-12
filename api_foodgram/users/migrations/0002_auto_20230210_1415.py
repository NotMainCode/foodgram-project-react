# Generated by Django 2.2.28 on 2023-02-10 11:15

import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="subscription",
            constraint=models.CheckConstraint(
                check=models.Q(
                    _negated=True,
                    user=django.db.models.expressions.F("author"),
                ),
                name="subscriber_not_author",
            ),
        ),
    ]