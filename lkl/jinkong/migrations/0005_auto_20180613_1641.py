# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-06-13 16:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jinkong', '0004_jksettlement'),
    ]

    operations = [
        migrations.CreateModel(
            name='JKPos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn_code', models.CharField(max_length=64, unique=True, verbose_name='SN\u53f7')),
                ('terminal', models.CharField(blank=True, max_length=64, verbose_name='\u7ec8\u7aef\u53f7')),
                ('is_activate', models.BooleanField(default=False, verbose_name='\u662f\u5426\u6fc0\u6d3b')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7528\u6237')),
            ],
            options={
                'db_table': 'jk_pos',
                'verbose_name': '\u7528\u6237POS\u673a',
                'verbose_name_plural': '\u7528\u6237POS\u673a',
            },
        ),
        migrations.AlterModelOptions(
            name='jksettlement',
            options={'ordering': ['-update_time'], 'verbose_name': '\u5546\u6237\u7ed3\u7b97\u5355\u67e5\u8be2', 'verbose_name_plural': '\u5546\u6237\u7ed3\u7b97\u5355\u67e5\u8be2'},
        ),
    ]