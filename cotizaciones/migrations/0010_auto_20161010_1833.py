# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-10 23:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0009_auto_20161005_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='total',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='cantidad',
            field=models.DecimalField(decimal_places=3, max_digits=18),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='precio',
            field=models.DecimalField(decimal_places=0, max_digits=18),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='total',
            field=models.DecimalField(decimal_places=0, max_digits=18),
        ),
    ]
