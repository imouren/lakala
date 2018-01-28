# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-28 13:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LKLTrade01',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchantCode', models.CharField(max_length=64, verbose_name='\u5546\u6237\u7f16\u7801')),
                ('maintainOrg', models.CharField(max_length=64, verbose_name='\u4ee3\u7406\u5546')),
                ('transId', models.CharField(max_length=64, unique=True, verbose_name='\u6d41\u6c34\u53f7')),
                ('cardType', models.CharField(max_length=64, verbose_name='\u6e20\u9053')),
                ('transCode', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u53f7')),
                ('termNo', models.CharField(max_length=64, verbose_name='\u7ec8\u7aef\u53f7')),
                ('payAmt', models.CharField(max_length=64, verbose_name='\u4ed8\u6b3e\u91d1\u989d\uff08\u5206\uff09')),
                ('cardNo', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u5361\u53f7')),
                ('feeAmt', models.CharField(max_length=64, verbose_name='\u624b\u7eed\u8d39')),
                ('sid', models.CharField(max_length=64, verbose_name='SID')),
                ('merchantName', models.CharField(max_length=64, verbose_name='\u5546\u6237\u540d\u79f0')),
                ('transType', models.CharField(max_length=64, verbose_name='\u4e1a\u52a1\u7c7b\u578b')),
                ('signimage', models.CharField(max_length=1024, verbose_name='\u7b7e\u8d2d\u5355')),
                ('transAmt', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u91d1\u989d\uff08\u5143\uff09')),
                ('trade_date', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u65f6\u95f4')),
            ],
            options={
                'db_table': 'lkl_trade01',
                'verbose_name': '\u6536\u6b3e\u4ea4\u6613',
                'verbose_name_plural': '\u6536\u6b3e\u4ea4\u6613',
            },
        ),
        migrations.CreateModel(
            name='UserAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, verbose_name='\u6536\u4ef6\u4eba')),
                ('phone', models.CharField(max_length=20, verbose_name='\u624b\u673a')),
                ('telephone', models.CharField(blank=True, max_length=20, verbose_name='\u5ea7\u673a')),
                ('area1', models.CharField(max_length=50, verbose_name='\u7701')),
                ('area2', models.CharField(max_length=50, verbose_name='\u5e02')),
                ('area3', models.CharField(max_length=50, verbose_name='\u53bf')),
                ('address', models.CharField(max_length=250, verbose_name='\u5177\u4f53\u5730\u5740')),
                ('post_code', models.CharField(blank=True, max_length=20, verbose_name='\u90ae\u7f16')),
                ('is_default', models.BooleanField(default=False, verbose_name='\u662f\u5426\u9ed8\u8ba4\u5730\u5740')),
                ('is_disabled', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7981\u7528')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7528\u6237')),
            ],
            options={
                'db_table': 'user_address',
                'verbose_name': '\u7528\u6237\u5730\u5740',
                'verbose_name_plural': '\u7528\u6237\u5730\u5740',
            },
        ),
        migrations.CreateModel(
            name='UserPos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, verbose_name='POS\u5e8f\u5217\u53f7')),
                ('first_bound', models.BooleanField(default=False, verbose_name='\u662f\u5426\u7b2c\u4e00\u6b21\u7ed1\u5b9a')),
                ('is_activate', models.BooleanField(default=False, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7528\u6237')),
            ],
            options={
                'db_table': 'user_pos',
                'verbose_name': '\u7528\u6237POS\u673a',
                'verbose_name_plural': '\u7528\u6237POS\u673a',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=20, unique=True, verbose_name='\u624b\u673a')),
                ('name', models.CharField(max_length=20, verbose_name='\u59d3\u540d')),
                ('sex', models.CharField(choices=[(b'F', '\u5973'), (b'M', '\u7537'), (b'O', '\u5176\u4ed6')], max_length=1, verbose_name='\u6027\u522b')),
                ('is_vip', models.BooleanField(default=False, verbose_name='\u662f\u5426VIP')),
                ('code', models.CharField(max_length=36, unique=True, verbose_name='\u9080\u8bf7\u7801')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('father', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to=settings.AUTH_USER_MODEL, verbose_name='\u4e0a\u5bb6')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'user_profile',
                'verbose_name': '\u7528\u6237\u5c5e\u6027',
                'verbose_name_plural': '\u7528\u6237\u5c5e\u6027',
            },
        ),
        migrations.CreateModel(
            name='UserTrade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trade_type', models.CharField(choices=[(b'ya', '\u4ea4\u62bc\u91d1'), (b'tui', '\u9000\u62bc\u91d1'), (b'fen', '\u5206\u7ea2')], max_length=50, verbose_name='\u4ea4\u6613\u7c7b\u578b')),
                ('rmb', models.IntegerField(verbose_name='\u91d1\u989d')),
                ('message', models.TextField(verbose_name='\u8bf4\u660e')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7528\u6237')),
            ],
            options={
                'db_table': 'user_trade',
                'verbose_name': '\u7528\u6237\u4ea4\u6613\u8bb0\u5f55',
                'verbose_name_plural': '\u7528\u6237\u4ea4\u6613\u8bb0\u5f55',
            },
        ),
    ]
