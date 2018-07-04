# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('comment', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('dateFrom', models.CharField(max_length=255)),
                ('balance', models.CharField(max_length=255)),
            ],
        ),
    ]
