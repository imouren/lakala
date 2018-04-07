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


def home(request):
    """
    用户首页
    """
    data = {}
    return render(request, "lkl/index.html", data)


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
