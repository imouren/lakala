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
from .forms import LoginForm, RegisterForm, UserPosForm, UserAlipayForm, TixianRMBForm
from .models import UserProfile, UserPos, UserAlipay, UserFenRun, FenRunOrder, TiXianOrder, WXUser
from . import utils, dbutils
from lkl import config, wx_utils
from .utils import rclient

logger = logging.getLogger('statistics')


def home_bak(request):
    """
    用户首页
    微信登陆，判断是否绑定过
    绑定过自动登录 同时更新微信用户信息
    """
    data = {}
    return render(request, "lkl/index.html", data)


def home(request):
    """
    用户首页
    """
    key = 'lkl_home'
    data_str = rclient.get(key)
    if not data_str:
        items = dbutils.get_user_pos_top()
        data_str = pickle.dumps(items)
        rclient.set(key, data_str)
        rclient.expire(key, 3600)
    else:
        items = pickle.loads(data_str)
    data = {"items": items}
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
    # 支付宝信息
    alipays = user.useralipay_set.values("account", "name")
    if alipays:
        alipay = alipays[0]
    else:
        alipay = None
    # 刷卡总额和秒到笔数
    if fenrun:
        d0_num, freeze_num = dbutils.get_user_d0_num(user)
    else:
        d0_num = 0
        freeze_num = 0
    d1_totoal, freeze_total = dbutils.get_user_d1_total(user)
    rmb, child_rmb = dbutils.get_userrmb_num(user)
    txz_rmb = dbutils.get_user_txz_rmb(user)
    data = {
        "fenrun": fenrun,
        "d0_num": d0_num,
        "d0_freeze_num": freeze_num,
        "d1_total": d1_totoal,
        "d1_freeze_total": freeze_total,
        "txz_rmb": "%.2f" % (txz_rmb / 100.0),
        "rmb": "%.2f" % (rmb / 100.0),
        "child_rmb": "%.2f" % (child_rmb / 100.0),
        "alipay": alipay
    }
    return render(request, "lkl/user_info.html", data)


@login_required
def alipay(request):
    # 已经绑定过
    objs = request.user.useralipay_set.values()
    if len(objs) > 0:
        return redirect("user_info")
    data = {}
    if request.method == 'POST':
        form = UserAlipayForm(request.POST, request=request)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            name = form.cleaned_data.get('name')
            UserAlipay.objects.create(user=request.user, account=account, name=name)
            return redirect("user_info")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/user_alipay.html", data)


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
    pos_list = []
    for pos in poses:
        status = dbutils.get_terminal_status(pos)
        tmp = {
            "code": pos,
            "status": status
        }
        pos_list.append(tmp)
    data = {"poses": pos_list}
    return render(request, "lkl/pos_list.html", data)


@login_required
def pos_detail(request):
    pos = request.GET.get("pos")
    poses = utils.get_user_poses(request.user)
    pos_detail = []
    if pos in poses:
        pos_detail = dbutils.get_pos_d1_detail(pos)
    data = {"detail": pos_detail}
    return render(request, "lkl/pos_detail.html", data)


@login_required
def friend_list(request):
    friends_01_d1_total = []
    pos_status_list = []
    friends_01 = list(request.user.children.all())
    friends_01.sort(key=lambda x: x.create_time)
    friends_02 = []
    for obj in friends_01:
        d1_totoal, freeze_total = dbutils.get_user_d1_total(obj.user)
        friends_01_d1_total.append(d1_totoal)
        poses = dbutils.get_user_pos(obj.user)
        jihuo, dabiao = dbutils.get_pos_status_num(poses)
        pos_status_list.append((len(poses), jihuo, dabiao))
        friends = list(obj.user.children.all())
        friends_02.extend(friends)
    friends = zip(friends_01, friends_01_d1_total, pos_status_list)
    data = {"friends": friends, "friends_02": friends_02}
    return render(request, "lkl/friend_list.html", data)


@login_required
def tixian_rmb(request):
    data = {"order_type": "RMB"}
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    user = request.user
    # 支付宝账户
    alipays = user.useralipay_set.values("account", "name")
    if alipays:
        alipay = alipays[0]
    else:
        alipay = None
    if alipay is None:
        return redirect("user_alipay")
    data["user_account"] = u"支付宝：%s__%s" % (alipay["account"], alipay["name"])

    if request.method == 'POST':
        # 禁止提现用户
        if user.username in config.DISABLE_TIXIN:
            error = [u"您是合伙人，不允许平台提现"]
            data.update({"error": error})
            return render(request, "lkl/tixian_rmb.html", data)
        # 操作频繁
        key = 'lkl_tixian_locked_%s' % (user.id)
        locked = rclient.get(key)
        if locked:
            error = [u"操作太频繁"]
            data.update({"error": error})
            return render(request, "lkl/tixian_rmb.html", data)
        else:
            rclient.set(key, True)
            rclient.expire(key, 10)
        # 未结算订单
        if not dbutils.can_tixian(user):
            error = [u"提现间隔大于1分钟且无提现中订单"]
            data.update({"error": error})
            return render(request, "lkl/tixian_rmb.html", data)
        # 正式流程
        data.update(request.POST.dict())
        form = TixianRMBForm(data)
        if form.is_valid():
            tx = form.save(commit=False)
            # 判断钱够不够
            my_rmb, _ = dbutils.get_userrmb_num(user)
            if my_rmb < tx.rmb:
                error = [u"余额不足"]
                data.update({"error": error})
            else:
                tx.user = user
                tx.fee = int(tx.rmb * 0.1)
                tx.save()
                # 扣钱
                dbutils.sub_userrmb_rmb(user, tx.rmb)
                tx.pay_time = datetime.now()
                tx.status = "PD"
                tx.save()
                return redirect("user_info")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    return render(request, "lkl/tixian_rmb.html", data)


@login_required
def tixian_child_rmb(request):
    data = {"order_type": "CHILD_RMB"}
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    user = request.user
    # 支付宝账户
    alipays = user.useralipay_set.values("account", "name")
    if alipays:
        alipay = alipays[0]
    else:
        alipay = None
    if alipay is None:
        return redirect("user_alipay")
    data["user_account"] = u"支付宝：%s__%s" % (alipay["account"], alipay["name"])

    if request.method == 'POST':
        # 禁止提现用户
        if user.username in config.DISABLE_TIXIN:
            error = [u"您是合伙人，不允许平台提现"]
            data.update({"error": error})
            return render(request, "lkl/tixian_child_rmb.html", data)
        # 操作频繁
        key = 'lkl_tixian_locked_%s' % (user.id)
        locked = rclient.get(key)
        if locked:
            error = [u"操作太频繁"]
            data.update({"error": error})
            return render(request, "lkl/tixian_child_rmb.html", data)
        else:
            rclient.set(key, True)
            rclient.expire(key, 10)
        # 未结算订单
        if not dbutils.can_tixian(user):
            error = [u"提现间隔大于1分钟且无提现中订单"]
            data.update({"error": error})
            return render(request, "lkl/tixian_child_rmb.html", data)
        # 正式流程
        data.update(request.POST.dict())
        form = TixianRMBForm(data)
        if form.is_valid():
            tx = form.save(commit=False)
            # 判断钱够不够
            _, my_rmb = dbutils.get_userrmb_num(user)
            if my_rmb < tx.rmb:
                error = [u"余额不足"]
                data.update({"error": error})
            else:
                tx.user = user
                tx.fee = int(tx.rmb * 0.1)
                tx.save()
                # 扣钱
                dbutils.sub_userrmb_rmb(user, tx.rmb, True)
                tx.pay_time = datetime.now()
                tx.status = "PD"
                tx.save()
                return redirect("user_info")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    return render(request, "lkl/tixian_child_rmb.html", data)


@login_required
def tixian_list(request):
    user = request.user
    objs = TiXianOrder.objects.filter(user=user).filter(status="SU")
    data = {"items": objs}
    return render(request, "lkl/tixian_list.html", data)


@login_required
def set_fenrun(request, child):
    data = {}
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    user = request.user
    # 分润
    if hasattr(user, "userfenrun"):
        f_point = float(user.userfenrun.point)
        f_rmb = float(user.userfenrun.rmb)
        point_list = [x[0] for x in UserFenRun.POINT_CHOICE if float(x[0]) <= f_point]
        rmb_list = [x[0] for x in UserFenRun.RMB_CHOICE if float(x[0]) <= f_rmb]
        child_fenrun = {
            "point": json.dumps(point_list),
            "rmb": json.dumps(rmb_list)
        }
    else:
        child_fenrun = {}
    data.update(child_fenrun)

    if request.method == 'POST':
        # 操作频繁
        key = 'lkl_setfenrun_locked_%s' % (user.id)
        locked = rclient.get(key)
        if locked:
            error = [u"操作太频繁"]
            data.update({"error": error})
            return render(request, "lkl/set_fenrun.html", data)
        else:
            rclient.set(key, True)
            rclient.expire(key, 10)
        # 数值判断
        point = request.POST.get("point")
        rmb = request.POST.get("rmb")
        if point not in point_list or rmb not in rmb_list:
            error = [u"分润点或者秒到点错误"]
            data.update({"error": error})
            return render(request, "lkl/set_fenrun.html", data)
        # 关系判断
        child_user = utils.get_user_by_username(child)
        children = [obj.phone for obj in request.user.children.all()]
        if not child_user or child not in children:
            error = [u"用户不存在或者不是您邀请来的"]
            data.update({"error": error})
            return render(request, "lkl/set_fenrun.html", data)
        # 分润提高判断
        if hasattr(child_user, "userfenrun"):
            old_point = float(child_user.userfenrun.point)
            old_rmb = float(child_user.userfenrun.rmb)
            if float(point) < float(old_point) or float(rmb) < float(old_rmb):
                error = [u"分润点和秒到点只允许提高"]
                data.update({"error": error})
                return render(request, "lkl/set_fenrun.html", data)
        # 判断是否已经有申请未审批，或者上次提交距离7天内
        sq = dbutils.get_last_fenren_order(user, child_user)
        if sq:
            if sq.status == "OK":
                now = datetime.now()
                diff = now - sq.create_time
                if diff.total_seconds() < 3600 * 24 * 30:
                    error = [u"30天内只能申请一次"]
                    data.update({"error": error})
                    return render(request, "lkl/set_fenrun.html", data)
            else:
                error = [u"该用户有未通过分润审核，请等待"]
                data.update({"error": error})
                return render(request, "lkl/set_fenrun.html", data)
        # 创建申请
        FenRunOrder.objects.create(
            user=user,
            child=child_user,
            point=point,
            rmb=rmb
        )
        return redirect("friend_list")
    return render(request, "lkl/set_fenrun.html", data)


def password_reset(request):
    data = {}
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/password_reset.html", data)


@login_required
def bind_wx(request):
    # 绑定微信
    # 判断已经绑定过
    user = request.user
    wx_user = dbutils.get_wx_user(user)
    if wx_user:
        wx_info = {
            "nickname": wx_user.nickname,
            "headimgurl": wx_user.headimgurl
        }
        return render(request, "lkl/wx_info.html", wx_info)
    # todo 判断用户profile有内容
    user = request.user
    state = user.username
    url = wx_utils.get_wx_authorize_url(config.WX_REDIRECT_URL, state)
    return redirect(url)


def wx_redirect(request):
    """
    info response
    {
    "openid":" OPENID",
    "nickname": NICKNAME,
    "sex":"1",
    "province":"PROVINCE"
    "city":"CITY",
    "country":"COUNTRY",
    "headimgurl":    "http://thirdwx.qlogo.cn/mmopen/g3MonUZtNHkdmzicIlibx6iaFqAc56vxLSUfpb6n5WKSYVY0ChQKkiaJSgQ1dZuTOgvLLrhJbERQQ4eMsv84eavHiaiceqxibJxCfHe/46",
    "privilege":[ "PRIVILEGE1" "PRIVILEGE2"     ],
    "unionid": "o6_bmasdasdsad6_2sgVt7hMZOPfL"
    }
    """
    # logger.info("wx_redirect")
    # logger.info(request.GET)
    code = request.GET.get("code")
    username = request.GET.get("state")
    user = dbutils.get_user_by_username(username)
    res = wx_utils.get_access_token(code)
    access_token = res["access_token"]
    openid = res["openid"]
    scope = res["scope"]
    # 判断openid 是否绑定过
    if scope == "snsapi_userinfo":
        # 通过access_token和openid拉取用户信息
        # info_res = wx_utils.get_sns_userinfo(access_token, openid)
        info_res = wx_utils.get_userinfo(access_token, openid)
        if not info["subscribe"]:
            return HttpResponse(u"未关注公众号，不允许绑定")
        # logger.info(info_res)
        # 创建绑定关系 带用户信息
        if not dbutils.is_bing_wx(user):
            WXUser.objects.create(
                user=user,
                openid=info_res["openid"],
                nickname=info_res["nickname"],
                sex=info_res["sex"],
                province=info_res["province"],
                city=info_res["city"],
                country=info_res["country"],
                headimgurl=info_res["headimgurl"],
                unionid=info_res.get("unionid", ""),
            )
    return HttpResponse(u"绑定成功")


def wx_redirect_login(request):
    """
    微信自动登陆回调
    """
    code = request.GET.get("code")
    uri = request.GET.get("state")
    res = wx_utils.get_access_token(code)
    # access_token = res["access_token"]
    openid = res["openid"]
    # scope = res["scope"]
    api_access_token = wx_utils.get_api_access_token()
    info = wx_utils.get_userinfo(api_access_token, openid)
    # 判断openid 是否关注过
    # 判断openid 是否绑定过
    if info["subscribe"]:
        wx_user = dbutils.get_wx_user_by_openid(openid)
        auth.login(request, wx_user.user)
    return redirect(uri)
