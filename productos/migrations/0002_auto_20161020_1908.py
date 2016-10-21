# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-21 00:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='con_nombre_automatico',
            field=models.BooleanField(default=True, verbose_name='nombre automático'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='descripcion_comercial',
            field=models.CharField(default='AUTOMATICO', max_length=200),
        ),
        migrations.AlterField(
            model_name='producto',
            name='descripcion_estandar',
            field=models.CharField(default='AUTOMATICO', max_length=200),
        ),
    ]