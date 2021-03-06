# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-06-15 16:25
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jinkong', '0005_auto_20180613_1641'),
    ]

    operations = [
        migrations.CreateModel(
            name='JKFenRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', models.CharField(choices=[(b'0.520', '0.520'), (b'0.525', '0.525'), (b'0.530', '0.530'), (b'0.535', '0.535'), (b'0.540', '0.540'), (b'0.545', '0.545'), (b'0.550', '0.550'), (b'0.555', '0.555'), (b'0.560', '0.560'), (b'0.565', '0.565'), (b'0.570', '0.570'), (b'0.575', '0.575'), (b'0.580', '0.580'), (b'0.585', '0.585'), (b'0.590', '0.590'), (b'0.595', '0.595'), (b'0.60', '0.60')], max_length=50, verbose_name='\u63d0\u70b9')),
                ('message', models.TextField(blank=True, verbose_name='\u8bf4\u660e')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u66f4\u65b0\u65f6\u95f4')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7528\u6237')),
            ],
            options={
                'db_table': 'jk_fenrun',
                'verbose_name': '\u91d1\u63a7\u4ed8\u5206\u6da6',
                'verbose_name_plural': '\u91d1\u63a7\u4ed8\u5206\u6da6',
            },
        ),
    ]
