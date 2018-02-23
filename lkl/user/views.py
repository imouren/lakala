# -*- coding: utf-8 -*-
import logging
import requests
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
from .forms import LoginForm, RegisterForm, UserPosForm
from .models import UserProfile, UserPos
from . import utils, dbutils
from lkl import config

logger = logging.getLogger('statistics')


def home(request):
    """
    用户首页
    """
    data = {}
    return render(request, "lkl/index.html", data)


def news(request):
    """
    资讯页
    """
    data = {}
    return render(request, "lkl/news.html", data)


def account(request):
    """
    账户页
    """
    data = {}
    if request.user.is_authenticated:
        return render(request, "lkl/account.html", data)
    else:
        return redirect("user_login")


def loginx(request):
    """
    登陆
    """

    if request.user.is_authenticated:
        return redirect("user_account")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                request.session['user_name'] = username
                return redirect("user_account")
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data = {"img_url": img_url, "hashkey": hashkey}
    return render(request, "lkl/login.html", data)


def login(request):
    data = {}
    if request.user.is_authenticated:
        return redirect("user_account")
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return redirect("user_account")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/login.html", data)


@login_required
def logout(request):
    auth.logout(request)
    return redirect("user_home")


def register(request):
    data = {}
    if request.user.is_authenticated:
        return redirect("user_account")
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            sex = form.cleaned_data.get('sex')
            name = form.cleaned_data.get('name')
            user = User.objects.create_user(username=username, password=password)
            user.save()
            UserProfile.objects.create(user=user, phone=user.username, sex=sex, name=name, father=form.get_father_user())
            auth.login(request, user)
            return redirect("user_account")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/register.html", data)


@login_required
def info(request):
    """
    我的信息
    """
    user = request.user
    # 分润
    if hasattr(user, "userfenrun"):
        fenrun = {"point": float(user.userfenrun.point), "rmb": float(user.userfenrun.rmb)}
    else:
        fenrun = None
    # 刷卡总额和秒到笔数
    if fenrun:
        d0_num = dbutils.get_user_d0_num(user)
    else:
        d0_num = 0
    d1_totoal = dbutils.get_user_d1_total(user)
    rmb, child_rmb = dbutils.get_userrmb_num(user)
    data = {"fenrun": fenrun, "d0_num": d0_num, "d1_total": d1_totoal, "rmb": "%.2f" % (rmb / 100.0), "child_rmb": "%.2f" % (child_rmb / 100.0)}
    return render(request, "lkl/user_info.html", data)


@login_required
def search_terminal(request):
    data = {}
    if request.method == 'POST':
        q = request.POST.get("q")
        s = request.POST.get("s")  # 是否显示搜索框
        trade_data = utils.get_d1_by_terminal(q)
        data["trade"] = trade_data
        data["s"] = s
    return render(request, "lkl/search_terminal.html", data)


@login_required
def bind_pos(request):
    data = {}
    if request.method == 'POST':
        form = UserPosForm(request.POST, request=request)
        if form.is_valid():
            print form.cleaned_data
            code = form.cleaned_data.get('code')
            UserPos.objects.create(user=request.user, code=code)
            return redirect("pos_list")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/bind_pos.html", data)


@login_required
def pos_list(request):
    poses = utils.get_user_poses(request.user)
    data = {"poses": poses}
    return render(request, "lkl/pos_list.html", data)


@login_required
def friend_list(request):
    freinds_01 = list(request.user.children.all())
    freinds_01.sort(key=lambda x: x.create_time)
    freinds_02 = []
    for obj in freinds_01:
        friends = list(obj.user.children.all())
        freinds_02.extend(friends)
    data = {"freinds_01": freinds_01, "freinds_02": freinds_02}
    return render(request, "lkl/friend_list.html", data)


@login_required
def bind_wx(request):
    # 获取
    # 重新授权或者第一次授权
    user = request.user
    base_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={}&redirect_uri={}&response_type=code&scope=snsapi_userinfo&state={}#wechat_redirect"
    rurl = quote_plus(config.WX_REDIRECT_URL)
    url = base_url.format(config.APP_ID, rurl, user.username)
    return redirect(url)


def wx_redirect(request):
    logger.info(request.GET)
    code = request.GET.get("code")
    username = request.GET.get("state")
    url_base = "https://api.weixin.qq.com/sns/oauth2/access_token?appid={}&secret={}&code={}&grant_type=authorization_code"
    url = url_base.format(config.APP_ID, config.APP_SECRET, code)
    res = requests.get(url).json()
    # 保存 openid access_token refresh_token 的到期时间
    # 保存openid 和 username对应关系 绑定时间
    # 获取用户信息，并保存数据库
    return HttpResponse("ok")
