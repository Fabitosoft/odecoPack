# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-10 16:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0013_auto_20161010_1104'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='margenprovedor',
            options={'verbose_name_plural': 'Margenes x Proveedores'},
        ),
    ]
