# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-13 13:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despachos_mercancias', '0006_auto_20170112_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='enviotransportadoratcc',
            name='fecha_entrega_boom',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='enviotransportadoratcc',
            name='nro_tracking_boom',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]