# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-03 19:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documentos', '0003_auto_20170103_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tipodocumento',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tipodocumento',
            name='nomenclatura',
            field=models.CharField(max_length=2, unique=True),
        ),
    ]