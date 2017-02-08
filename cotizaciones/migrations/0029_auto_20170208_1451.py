# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-08 19:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0028_auto_20170208_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotizacion',
            name='apellidos_contacto',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='cotizacion',
            name='email',
            field=models.EmailField(max_length=150),
        ),
        migrations.AlterField(
            model_name='cotizacion',
            name='nombres_contacto',
            field=models.CharField(max_length=120),
        ),
        migrations.AlterField(
            model_name='cotizacion',
            name='razon_social',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
