# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from . import site_utils
from .utils import rclient


# @cache_page(3600)
@staff_member_required
def income(request):
    """
    1. 当月总交易量
    2. 当月秒到笔数
    3. 当月公司盈利
    4. 已经提现、未提现
    5. 下级分点的提现和未提现
    """
    # 缓存
    key = 'lkl_income_page'
    data_str = rclient.get(key)
    if not data_str:
        pos_data = site_utils.get_boss_pos_info()
        d1_data = site_utils.get_boss_d1_info()
        d0_data = site_utils.get_boss_d0_info()
        urmb, child_urmb = site_utils.get_all_urmb()
        tx_rmb = site_utils.get_all_txrmb()
        data = {
            "d1_data": sorted(d1_data.iteritems()),
            "d0_data": sorted(d0_data.iteritems()),
            "pos_data": sorted(pos_data.iteritems()),
            "urmb": "%.2f" % (urmb / 100.0),
            "child_urmb": "%.2f" % (child_urmb / 100.0),
            "tx_rmb": "%.2f" % (tx_rmb / 100.0),
        }
        data_str = json.dumps(data)
        rclient.set(key, data_str)
        rclient.expire(key, 3600)
    else:
        data = json.loads(data_str)
    return render(request, "admin/income.html", data)


# @cache_page(3600)
@staff_member_required
def reminder(request):
    data = site_utils.get_reminder_data()
    render_data = {"data": data}
    return render(request, "admin/reminder.html", render_data)
