# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-06 13:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotizaciones', '0007_auto_20170105_1626'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcotizacion',
            name='p_n_lista_unidad_medida',
            field=models.CharField(max_length=120, null=True, verbose_name='Unidad Medida'),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='cantidad',
            field=models.DecimalField(decimal_places=3, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='p_n_lista_descripcion',
            field=models.CharField(max_length=120, null=True, verbose_name='Descripción Otro'),
        ),
        migrations.AlterField(
            model_name='itemcotizacion',
            name='p_n_lista_referencia',
            field=models.CharField(blank=True, max_length=120, null=True, verbose_name='Referencia Otro'),
        ),
    ]
