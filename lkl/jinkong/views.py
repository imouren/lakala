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
from . import dbutils
from lkl import wx_utils, config

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
    pos = request.GET.get("pos")
    pos_detail = dbutils.get_pos_prov(pos)
    data = {"detail": pos_detail}
    return render(request, "jinkong/pos_detail.html", data)


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
    # rmb = dbutils.get_jkuserrmb_num(user)
    data = {
        "fenrun": fenrun,
        "trans_total": trans_total,
        # "rmb": "%.2f" % (rmb / 100.0)
        "rmb": u"敬请期待！"
    }
    return render(request, "jinkong/user_info.html", data)
