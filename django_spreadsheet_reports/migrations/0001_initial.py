# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('uri', models.CharField(max_length=4096)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('slug', models.CharField(max_length=255)),
                ('date', models.DateField(auto_now_add=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('group_name', models.CharField(max_length=255)),
                ('group_val', models.IntegerField(default=0)),
                ('low_limit', models.IntegerField(default=0)),
                ('high_limit', models.IntegerField(default=0)),
                ('prev_val', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
