# -*- coding: utf-8 -*-
import json
import logging
import requests
import cPickle as pickle
from datetime import datetime
from urllib import quote_plus
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from . import dbutils, utils, models
from lkl import wx_utils, config
from prov_code import PROV_CODE

logger = logging.getLogger('statistics')


def home_login(request):
    scope = "snsapi_base"
    state = "jk_home"
    url = wx_utils.get_wx_authorize_url(config.WX_REDIRECT_URL_LOGIN, state, scope)
    return redirect(url)


@login_required
def home(request):
    """
    金控用户首页
    """
    data = {}
    return render(request, "jinkong/home.html", data)


@login_required
def jk_pos_list(request):
    poses = dbutils.get_user_poses(request.user)
    pos_list = []
    for sn, pos in poses:
        status = dbutils.get_terminal_status(pos)
        tmp = {
            "sn": sn,
            "code": pos,
            "status": status
        }
        pos_list.append(tmp)
    data = {"poses": pos_list}
    return render(request, "jinkong/pos_list.html", data)


@login_required
def jk_pos_detail(request):
    pos = request.GET.get("pos")
    pos_detail = dbutils.get_pos_detail(pos)
    data = {"detail": pos_detail}
    return render(request, "jinkong/pos_detail.html", data)


@login_required
def jk_merchant_prov(request):
    merchants = dbutils.get_user_merchants(request.user)
    merchant_objs = models.JKMerchant.objects.filter(merchant_code__in=merchants)
    merchant_prov_dict = utils.get_current_prov(merchants)
    merchant_list = []
    for obj in merchant_objs:
        info = {
            "merchant_code": obj.merchant_code,
            "merchant_name": obj.merchant_name,
            "prov": merchant_prov_dict.get(obj.merchant_code, "")
        }
        merchant_list.append(info)
    data = {"merchants": merchant_list}
    return render(request, "jinkong/merchant_prov.html", data)


@login_required
def jk_change_merchant_prov(request):
    merchant = request.GET.get("merchant")
    name = request.GET.get("name")
    data = {"merchant": merchant, "name": name, "prov_tuple": sorted(PROV_CODE.items())}
    if request.method == 'POST':
        merchant = request.POST.get("merchant")
        prov = request.POST.get("prov", "")
        merchants = dbutils.get_user_merchants(request.user)
        if merchant not in merchants:
            return redirect("jk_home")
        prov = prov.isdigit() and int(prov) or 0
        if prov in PROV_CODE:
            utils.change_prov(merchant, prov)
        return redirect("jk_merchant_prov")
    else:
        return render(request, "jinkong/change_merchant_prov.html", data)


@login_required
def info(request):
    """
    我的信息
    """
    user = request.user
    # 分润
    if hasattr(user, "jkfenrun"):
        point = float(user.jkfenrun.point)
        fenrun = {"point": point}
    else:
        fenrun = None
        point = 0.60
    trans_total = dbutils.get_user_trans_total(user)
    rmb = dbutils.get_jkuserrmb_num(user)
    tx_rmb = dbutils.get_jktxrmb_num(user)
    data = {
        "fenrun": fenrun,
        "trans_total": trans_total,
        "rmb": "%.2f" % (rmb / 100.0),
        "tx_rmb": "%.2f" % (tx_rmb / 100.0)
    }
    return render(request, "jinkong/user_info.html", data)


@login_required
def friend_list(request):
    friends_total = []
    pos_status_list = []
    friends = list(request.user.children.all())
    friends.sort(key=lambda x: x.create_time)
    for obj in friends:
        trans_total = dbutils.get_user_trans_total(obj.user)
        friends_total.append(trans_total)
        poses = dbutils.get_user_poses(obj.user)
        pose_num, dabiao_num = dbutils.get_pos_status_num(poses)
        pos_status_list.append((pose_num, dabiao_num))
    friends = zip(friends, friends_total, pos_status_list)
    data = {"friends": friends}
    return render(request, "jinkong/friend_list.html", data)
