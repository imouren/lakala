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

logger = logging.getLogger('statistics')


@login_required
def home(request):
    """
    星驿付用户首页
    """
    data = {}
    poses = dbutils.get_user_poses(request.user)
    if poses:
        return render(request, "xyf/home.html", data)
    else:
        return render(request, "lkl/index_bak.html", data)


@login_required
def xyf_pos_list(request):
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
    return render(request, "xyf/pos_list.html", data)


@login_required
def xyf_pos_detail(request):
    pos = request.GET.get("pos")
    pos_detail = dbutils.get_pos_detail(pos)
    data = {"detail": pos_detail}
    return render(request, "xyf/pos_detail.html", data)


@login_required
def info(request):
    """
    我的信息
    """
    user = request.user
    # 分润
    base_point = 0.55
    if hasattr(user, "xyffenrun"):
        point = float(user.xyffenrun.point)
        fenrun = {"point": point}
    else:
        fenrun = None
        point = 0.55
    trans_total = dbutils.get_user_trans_total(user)
    diff_point = base_point - point
    if diff_point > 0:
        rmb = float(trans_total) / 100.0 * diff_point
    else:
        rmb = 0
    data = {
        "fenrun": fenrun,
        "trans_total": trans_total,
        "rmb": "%.2f" % rmb,
    }
    return render(request, "xyf/user_info.html", data)
