# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-10 17:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0018_producto_margen'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='costo',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
    ]
