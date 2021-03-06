# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-20 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Moneda',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=20, unique=True)),
                ('cambio', models.DecimalField(decimal_places=4, default=0, max_digits=18)),
            ],
            options={
                'verbose_name_plural': '1. Monedas',
            },
        ),
    ]
