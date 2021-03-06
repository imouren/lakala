# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-08-30 19:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SDBToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField(verbose_name='token')),
                ('is_disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
            ],
            options={
                'ordering': ['-create_time'],
                'db_table': 'sdb_token',
                'verbose_name': '\u51ed\u8bc1',
                'verbose_name_plural': '\u51ed\u8bc1',
            },
        ),
        migrations.CreateModel(
            name='SDBTrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trans_id', models.CharField(max_length=64, unique=True, verbose_name='\u6d41\u6c34\u53f7')),
                ('merchant', models.CharField(max_length=64, verbose_name='\u5546\u6237\u53f7')),
                ('trade_date', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u65e5\u671f')),
                ('trade_rmb', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u91d1\u989d\uff08\u5143\uff09')),
                ('trade_type', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u7c7b\u578b')),
                ('trade_status', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u72b6\u6001')),
                ('card_code', models.CharField(max_length=64, verbose_name='\u5361\u53f7')),
                ('card_type', models.CharField(max_length=64, verbose_name='\u5361\u7c7b\u578b')),
                ('return_code', models.CharField(max_length=64, verbose_name='\u8fd4\u56de\u7801')),
                ('return_desc', models.CharField(max_length=64, verbose_name='\u8fd4\u56de\u7801\u63cf\u8ff0')),
                ('terminal', models.CharField(max_length=64, verbose_name='\u7ec8\u7aef\u53f7')),
                ('agent_level', models.CharField(max_length=64, verbose_name='\u4ee3\u7406\u5546\u7b49\u7ea7')),
                ('agent', models.CharField(max_length=64, verbose_name='\u4ee3\u7406\u5546\u53f7')),
                ('business_type', models.CharField(max_length=64, verbose_name='\u4e1a\u52a1\u7c7b\u578b')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u722c\u53d6\u66f4\u65b0\u65f6\u95f4')),
            ],
            options={
                'ordering': ['-trade_date'],
                'db_table': 'sdb_trade',
                'verbose_name': '\u4ea4\u6613\u660e\u7ec6',
                'verbose_name_plural': '\u4ea4\u6613\u660e\u7ec6',
            },
        ),
    ]
