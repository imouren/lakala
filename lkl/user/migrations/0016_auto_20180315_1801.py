# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-03-15 18:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_auto_20180306_1805'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fenrunorder',
            options={'ordering': ['-create_time'], 'verbose_name': '\u5206\u6da6\u7533\u8bf7\u8868', 'verbose_name_plural': '\u5206\u6da6\u7533\u8bf7\u8868'},
        ),
        migrations.AddField(
            model_name='lkld1',
            name='fee_max',
            field=models.CharField(default=b'', max_length=64, verbose_name='\u5c01\u9876\u624b\u7eed\u8d39'),
        ),
        migrations.AddField(
            model_name='lkld1',
            name='fee_rate',
            field=models.CharField(default=b'0.600%', max_length=64, verbose_name='\u5546\u6237\u624b\u7eed\u8d39\u7387'),
        ),
    ]
