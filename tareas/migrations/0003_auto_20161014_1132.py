# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-14 16:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tareas', '0002_auto_20161014_1128'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tarea',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='tarea',
            name='updated_by',
        ),
    ]
