# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-07-30 17:39
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jinkong', '0008_jkprofit_jktixianorder_jkuserrmb'),
    ]

    operations = [
        migrations.CreateModel(
            name='JKChildProfit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fenrun_point', models.CharField(blank=True, max_length=50, verbose_name='\u63d0\u70b9')),
                ('fenrun_father_point', models.CharField(blank=True, max_length=50, verbose_name='\u5bfc\u5e08\u63d0\u70b9')),
                ('child_rmb', models.IntegerField(default=0, verbose_name='\u5df2\u7ecf\u83b7\u5229\u91d1\u989d(\u5206)')),
                ('rmb', models.IntegerField(default=0, verbose_name='\u63a8\u8350\u91d1\u989d(\u5206)')),
                ('merchant_code', models.CharField(max_length=64, verbose_name='\u5546\u6237\u7f16\u53f7')),
                ('terminal', models.CharField(max_length=64, verbose_name='\u7ec8\u7aef\u53f7')),
                ('trade_date', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u65e5\u671f')),
                ('trade_rmb', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u91d1\u989d\uff08\u5143\uff09')),
                ('trade_status', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u72b6\u6001')),
                ('return_code', models.CharField(max_length=64, verbose_name='\u5e94\u7b54\u7801')),
                ('card_type', models.CharField(max_length=64, verbose_name='\u5361\u7c7b\u578b')),
                ('trade_fee', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u624b\u7eed\u8d39\uff08\u5143\uff09')),
                ('qingfen_rmb', models.CharField(max_length=64, verbose_name='\u6e05\u5206\u91d1\u989d')),
                ('trans_id', models.CharField(max_length=64, unique=True, verbose_name='\u6d41\u6c34\u53f7')),
                ('fenrun', models.CharField(max_length=64, verbose_name='\u5206\u6da6')),
                ('trade_category', models.CharField(max_length=64, verbose_name='\u4ea4\u6613\u7c7b\u522b')),
                ('product', models.CharField(max_length=64, verbose_name='\u4ea7\u54c1\u6807\u8bc6')),
                ('status', models.CharField(choices=[(b'UP', '\u672a\u652f\u4ed8'), (b'PD', '\u5df2\u652f\u4ed8'), (b'SU', '\u6210\u529f')], default=b'UP', max_length=10, verbose_name='\u8ba2\u5355\u72b6\u6001')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('pay_time', models.DateTimeField(blank=True, null=True, verbose_name='\u5206\u7ea2\u65f6\u95f4')),
                ('father', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='father', to=settings.AUTH_USER_MODEL, verbose_name='\u5bfc\u5e08')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='\u7528\u6237')),
            ],
            options={
                'ordering': ['-pay_time'],
                'db_table': 'jk_child_user_profit',
                'verbose_name': '\u63a8\u8350\u7528\u6237\u83b7\u5229\u8868',
                'verbose_name_plural': '\u63a8\u8350\u7528\u6237\u83b7\u5229\u8868',
            },
        ),
    ]
