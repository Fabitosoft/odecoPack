# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-10 20:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandas', '0023_auto_20161007_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='ensamblado',
            name='precio_linea',
            field=models.DecimalField(decimal_places=4, default=0, editable=False, max_digits=10),
        ),
    ]
