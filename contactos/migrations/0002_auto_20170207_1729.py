# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-07 22:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contactos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactoempresa',
            name='correo_electronico',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]
