# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-06 20:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0054_auto_20170203_1211'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimientoventabiable',
            name='proyecto',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='facturasbiable',
            name='cliente',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='mis_compras', to='biable.Cliente'),
        ),
        migrations.RemoveField(
            model_name='facturasbiable',
            name='proyecto',
        ),
        migrations.AlterUniqueTogether(
            name='facturasbiable',
            unique_together=set([('tipo_documento', 'nro_documento')]),
        ),
    ]
