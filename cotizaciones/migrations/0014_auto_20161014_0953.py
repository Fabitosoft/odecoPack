# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-14 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0013_auto_20161014_0815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='fecha_envio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
