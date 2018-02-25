# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-24 13:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_useralipay'),
    ]

    operations = [
        migrations.AddField(
            model_name='tixianorder',
            name='finish_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='\u5b8c\u7ed3\u65f6\u95f4'),
        ),
        migrations.AddField(
            model_name='tixianorder',
            name='is_disabled',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528'),
        ),
        migrations.AddField(
            model_name='tixianorder',
            name='order_type',
            field=models.CharField(choices=[(b'RMB', '\u8fd4\u5229\u4f59\u989d\u63d0\u73b0'), (b'CHILD_RMB', '\u63a8\u8350\u4f59\u989d\u63d0\u73b0')], default=b'RMB', max_length=20, verbose_name='\u63d0\u73b0\u7c7b\u578b'),
        ),
        migrations.AddField(
            model_name='tixianorder',
            name='user_account',
            field=models.CharField(blank=True, max_length=512, verbose_name='\u7528\u6237\u8d26\u53f7'),
        ),
    ]