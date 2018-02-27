# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from . import site_utils


@staff_member_required
def income(request):
    """
    1. 当月总交易量
    2. 当月秒到笔数
    3. 当月公司盈利
    4. 已经提现、未提现
    5. 下级分点的提现和未提现
    """
    d1_data = site_utils.get_boss_d1_info()
    d0_data = site_utils.get_boss_d0_info()
    urmb, child_urmb = site_utils.get_all_urmb()
    tx_rmb = site_utils.get_all_txrmb()
    data = {
        "d1_data": d1_data,
        "d0_data": d0_data,
        "urmb": "%.2f" % (urmb / 100.0),
        "child_urmb": "%.2f" % (child_urmb / 100.0),
        "tx_rmb": "%.2f" % (tx_rmb / 100.0),
    }
    return render(request, "admin/income.html", data)
