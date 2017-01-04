# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-04 20:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('biable', '0028_auto_20170104_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendedorbiable',
            name='colaborador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='mi_vendedor_biable', to='usuarios.Colaborador'),
        ),
        migrations.AlterField(
            model_name='vendedorbiableuser',
            name='usuario',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mis_vendedores', to='usuarios.Colaborador'),
        ),
    ]