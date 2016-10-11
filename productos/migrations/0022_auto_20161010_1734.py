# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-10 22:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0021_auto_20161010_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='activo_catalogo',
            field=models.BooleanField(default=True, verbose_name='En Cata.'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='activo_componentes',
            field=models.BooleanField(default=True, verbose_name='En Compo.'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='activo_ensamble',
            field=models.BooleanField(default=False, verbose_name='Para Ensam.'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='activo_proyectos',
            field=models.BooleanField(default=True, verbose_name='En Proy.'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='margen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='productos_con_margen', to='proveedores.MargenProvedor', verbose_name='Id MxC'),
        ),
    ]
