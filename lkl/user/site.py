# -*- coding: utf-8 -*-
import cPickle as pickle
import requests
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from . import site_utils
from .utils import rclient
from jinkong.models import JKToken
from lkl import config

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    'Content-type': 'application/x-www-form-urlencoded',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) C,hrome/43.0.2357.124 Safari/537.36",
}

jk_session = requests.Session()


def template_variable(request):
    context = {
        "site_title": config.SITE_TITLE,
        "site_bottom_name": config.SITE_BOTTOM_NAME,
        "site_bottom_desc": config.SITE_BOTTOM_DESC
    }
    return context


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
    key = '%s_income_page' % config.SITE
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
        data_str = pickle.dumps(data)
        rclient.set(key, data_str)
        rclient.expire(key, 3600)
    else:
        data = pickle.loads(data_str)
    return render(request, "admin/income.html", data)


# @cache_page(3600)
@staff_member_required
def reminder(request):
    data = site_utils.get_reminder_data()
    render_data = {"data": data}
    return render(request, "admin/reminder.html", render_data)


@staff_member_required
def jk_income(request):
    """
    金控
    """
    # 缓存
    key = '%s_jk_income_page' % config.SITE
    data_str = rclient.get(key)
    if not data_str:
        pos_data = site_utils.get_jk_boss_pos_info()
        d1_data = site_utils.get_jk_boss_trade_info()
        urmb, child_urmb = site_utils.get_jk_all_urmb()
        tx_rmb = site_utils.get_jk_all_txrmb()
        data = {
            "d1_data": sorted(d1_data.iteritems()),
            "pos_data": sorted(pos_data.iteritems()),
            "urmb": "%.2f" % (urmb / 100.0),
            "child_urmb": "%.2f" % (child_urmb / 100.0),
            "tx_rmb": "%.2f" % (tx_rmb / 100.0),
        }
        data_str = pickle.dumps(data)
        rclient.set(key, data_str)
        rclient.expire(key, 3600)
    else:
        data = pickle.loads(data_str)
    return render(request, "admin/jk_income.html", data)


@staff_member_required
def jk_token_index(request):

    objs = JKToken.objects.filter(is_disabled=False)
    if objs:
        ok = True
    else:
        ok = False
    data = {"ok": ok}
    return render(request, "admin/jk_token_index.html", data)


@staff_member_required
def jk_token(request):
    code = request.POST.get("code")
    if code:
        data = {
            "userName": config.JK_NAME,
            "password": config.JK_PASS,
            "confirmationCode": code
        }
        res = jk_session.post("http://119.18.194.36/toHomePage.do", data=data, headers=HEADERS, verify=False)
        if "changeImg" not in res.content:
            cookies = jk_session.cookies
            cookies_str = ";".join(["=".join(item) for item in cookies.items()])
            JKToken.objects.create(token=cookies_str)
    return redirect("admin_jk_token_index")


def jk_token_pic(request):
    url = "http://119.18.194.36/image.do"
    response = jk_session.get(url, headers=HEADERS, verify=False)
    return HttpResponse(response.content, content_type='image/jpeg')
