# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-06 22:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bandas', '0004_valorcaracteristica_caracteristica'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banda',
            name='serie',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bandas.ValorCaracteristica'),
        ),
    ]
