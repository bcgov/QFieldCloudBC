# Generated by Django 3.2 on 2021-04-19 10:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import qfieldcloud.core.models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0031_auto_20210415_1535"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="organization",
            managers=[
                ("objects", qfieldcloud.core.models.OrganizationManager()),
            ],
        ),
        migrations.AddField(
            model_name="organizationmember",
            name="is_public",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="project",
            name="owner",
            field=models.ForeignKey(
                limit_choices_to=models.Q(user_type__in=[1, 2]),
                on_delete=django.db.models.deletion.CASCADE,
                related_name="projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
