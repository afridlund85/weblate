# Copyright © Michal Čihař <michal@weblate.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

# Generated by Django 3.0.7 on 2020-07-23 12:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trans", "0091_json_key"),
    ]

    operations = [
        migrations.AddField(
            model_name="alert",
            name="dismissed",
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
