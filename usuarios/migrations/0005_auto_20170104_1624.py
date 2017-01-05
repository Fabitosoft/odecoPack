# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-04 21:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0004_auto_20170104_1548'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='colaborador',
            name='subalternos',
        ),
        migrations.AddField(
            model_name='colaborador',
            name='subalternos',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='mi_jefe', to='usuarios.Colaborador'),
        ),
    ]