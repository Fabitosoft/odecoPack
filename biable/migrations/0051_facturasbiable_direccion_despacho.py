# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-02-03 14:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0050_auto_20170203_0858'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturasbiable',
            name='direccion_despacho',
            field=models.CharField(blank=True, max_length=400, null=True),
        ),
    ]