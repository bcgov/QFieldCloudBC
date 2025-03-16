# Generated by Django 2.2.17 on 2021-01-06 15:43

import django.core.validators
from django.db import migrations, models

import qfieldcloud.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0009_geodb"),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(
                help_text="Project name",
                max_length=255,
                validators=[
                    django.core.validators.RegexValidator(
                        "^[-a-zA-Z0-9_]+$",
                        "Only letters, numbers, underscores or hyphens are allowed.",
                    ),
                    django.core.validators.RegexValidator(
                        "^.{3,}$", "The name must be at least 3 characters long."
                    ),
                    django.core.validators.RegexValidator(
                        "^[a-zA-Z].*$", "The name must begin with a letter."
                    ),
                    qfieldcloud.core.validators.reserved_words_validator,
                ],
            ),
        ),
    ]
