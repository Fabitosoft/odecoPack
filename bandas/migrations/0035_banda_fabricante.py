# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-12 19:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bandas', '0034_remove_banda_uno'),
    ]

    operations = [
        migrations.AddField(
            model_name='banda',
            name='fabricante',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='bandas_con_fabricante', to='bandas.ValorCaracteristica'),
            preserve_default=False,
        ),
    ]
