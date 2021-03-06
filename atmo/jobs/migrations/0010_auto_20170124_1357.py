# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-01-24 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_sparkjob_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkjob',
            name='emr_release',
            field=models.CharField(choices=[(b'5.2.1', b'5.2.1'), (b'5.0.0', b'5.0.0'), (b'4.5.0', b'4.5.0')], default=b'5.2.1', help_text=b'Different EMR versions have different versions of software like Hadoop, Spark, etc', max_length=50, verbose_name=b'EMR release version'),
        ),
    ]
