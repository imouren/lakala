# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-06-08 17:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jinkong', '0002_jktoken'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='jkterminal',
            options={'ordering': ['-storage_date'], 'verbose_name': '\u7ec8\u7aef\u8bbe\u5907', 'verbose_name_plural': '\u7ec8\u7aef\u8bbe\u5907'},
        ),
        migrations.AddField(
            model_name='jktrade',
            name='fenrun',
            field=models.CharField(default='', max_length=64, verbose_name='\u5206\u6da6'),
            preserve_default=False,
        ),
    ]