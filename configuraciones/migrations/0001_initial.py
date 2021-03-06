# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-05 21:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DominiosEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dominio', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='EmailConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_ventas_from', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
                'verbose_name': 'Correos Electrónicos',
            },
        ),
    ]
