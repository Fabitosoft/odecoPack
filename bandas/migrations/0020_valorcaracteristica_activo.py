# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandas', '0019_auto_20161007_1126'),
    ]

    operations = [
        migrations.AddField(
            model_name='valorcaracteristica',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
