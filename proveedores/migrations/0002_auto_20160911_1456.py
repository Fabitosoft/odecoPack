# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-11 19:56
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proveedor',
            options={'verbose_name_plural': 'proveedores'},
        ),
    ]