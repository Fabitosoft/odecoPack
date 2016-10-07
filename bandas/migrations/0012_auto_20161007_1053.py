# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-07 15:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bandas', '0011_auto_20161007_1047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banda',
            name='ancho',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8, verbose_name='Ancho (mm)'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banda',
            name='color',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bandas_con_color', to='bandas.ValorCaracteristica'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banda',
            name='longitud',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8, verbose_name='Longitud (mm)'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banda',
            name='material',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bandas_con_material', to='bandas.ValorCaracteristica'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banda',
            name='material_varilla',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bandas_con_material_varilla', to='bandas.ValorCaracteristica'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banda',
            name='serie',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bandas_con_serie', to='bandas.ValorCaracteristica'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='banda',
            name='tipo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bandas_con_tipo', to='bandas.ValorCaracteristica'),
            preserve_default=False,
        ),
    ]
