# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-20 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0014_actualizacion'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimientoventabiable',
            name='nro_documento',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='movimientoventabiable',
            name='tipo_documento',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]