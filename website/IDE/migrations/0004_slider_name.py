# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-02-16 16:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IDE', '0003_auto_20210216_1723'),
    ]

    operations = [
        migrations.AddField(
            model_name='slider',
            name='name',
            field=models.CharField(default='def_name', max_length=50),
        ),
    ]
