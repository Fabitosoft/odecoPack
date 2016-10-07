# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-06 22:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bandas', '0006_auto_20161006_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='valorcaracteristica',
            name='caracteristica',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='bandas.Caracteristica'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='valorcaracteristica',
            name='nomenclatura',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
