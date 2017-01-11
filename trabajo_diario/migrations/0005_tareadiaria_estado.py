# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-10 17:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trabajo_diario', '0004_remove_trabajodia_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='tareadiaria',
            name='estado',
            field=models.PositiveIntegerField(choices=[(0, 'Pendiente'), (1, 'Atendida en Proceso'), (2, 'Atendida Terminada')], default=0),
        ),
    ]