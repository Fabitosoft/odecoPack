# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-13 13:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('despachos_mercancias', '0007_auto_20170113_0828'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enviotransportadoratcc',
            name='rr',
        ),
    ]
