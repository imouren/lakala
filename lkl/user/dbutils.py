# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.contrib.auth.models import User
from . import models
from . import utils
from lkl.utils import string_to_datetime


def add_userrmb_rmb(user, rmb, is_child=False):
    with transaction.atomic():
        obj, created = models.UserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        if is_child:
            obj.child_rmb += rmb
        else:
            obj.rmb += rmb
        obj.save()


def sub_userrmb_rmb(user, rmb, is_child=False):
    with transaction.atomic():
        obj, created = models.UserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        if is_child:
            obj.child_rmb -= rmb
        else:
            obj.rmb -= rmb
        obj.save()


def get_userrmb_num(user):
    with transaction.atomic():
        obj, created = models.UserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
    return obj.rmb, obj.child_rmb


def get_user_by_terminal(terminal):
    """
    通过终端号获取用户
    """
    try:
        obj = models.UserPos.objects.get(code=terminal)
        user = obj.user
    except Exception:
        user = None
    return user


def get_user_by_username(username):
    """
    通过昵称获取用户
    """
    try:
        user = User.objects.get(username=username)
    except Exception:
        user = None
    return user


def get_user_by_mcode(mcode):
    """
    通过商户号获取用户
    """
    objs = models.LKLTerminal.objects.filter(merchant_code=mcode)
    if len(objs) == 0:
        return None
    elif len(objs) > 1:
        return "multi"
    else:
        pos = objs[0].terminal
        return get_user_by_terminal(pos)


def get_user_pos(user):
    """
    获取用户终端号
    """
    poses = models.UserPos.objects.filter(user=user).values_list("code", flat=True)
    return list(poses)


def get_pos_status_num(poses):
    objs = models.LKLTerminal.objects.filter(terminal__in=poses)
    dabiao = 0
    for obj in objs:
        if obj.is_ok == u"是":
            dabiao += 1
    return len(objs), dabiao


def get_pos_d1_detail(pos):
    detail = []
    objs = models.LKLD1.objects.filter(terminal=pos)
    trans_total = Decimal(0)
    fee_total = Decimal(0)
    for obj in objs:
        if obj.card_type == u"贷记卡":
            month = obj.pay_date[:7]
            if month <= "2018-01":
                continue
            # 100以下交易不计算
            if Decimal(obj.draw_rmb) < 100:
                continue
            trans_total += Decimal(obj.draw_rmb)
            fee_total += Decimal(obj.fee_rmb)
            tmp = {
                "draw_rmb": obj.draw_rmb,
                "fee_rmb": obj.fee_rmb,
                "pay_date": obj.pay_date
            }
            detail.append(tmp)
    # total = {
    #     "draw_rmb": obj.trans_total,
    #     "fee_rmb": obj.fee_total,
    #     "pay_date": u"总计"
    # }
    # detail.append(total)
    return detail


def get_user_mcode(user):
    """
    获取用户商户号
    """
    mcode_list = []
    pos_list = get_user_pos(user)
    mcode_dict = defaultdict(list)
    objs = models.LKLTerminal.objects.filter(terminal__in=pos_list)
    for obj in objs:
        mcode_dict[obj.merchant_code].append(obj.terminal)
    for mcode, poses in mcode_dict.iteritems():
        if len(poses) == 1:
            mcode_list.append(mcode)
        else:
            ok_list = [pos in pos_list for pos in poses]
            if all(ok_list):
                mcode_list.append(mcode)
    return mcode_list


def get_user_d0_num(user):
    """
    获取用户D0笔数
    """
    freeze_n = 0
    end_datetime = datetime.now() - timedelta(4)
    end_day = "{}{:02}{:02}".format(end_datetime.year, end_datetime.month, end_datetime.day)
    mcode_list = get_user_mcode(user)
    objs = models.LKLD0.objects.filter(merchant_code__in=mcode_list).filter(fee_rmb="2").filter(trans_type=u"正交易").filter(trans_status=u"成功")
    for obj in objs:
        month = obj.draw_date[:6]
        day = obj.draw_date[:8]
        if month <= "201801":
            continue
        if day > end_day:
            freeze_n += 1
    return len(objs), freeze_n


def get_user_d1_total(user):
    """
    获取用户D1刷卡总额
    """
    end_datetime = datetime.now() - timedelta(4)
    trans_total = Decimal(0)
    freeze_total = Decimal(0)
    end_day = "{}-{:02}-{:02}".format(end_datetime.year, end_datetime.month, end_datetime.day)
    pos_list = get_user_pos(user)
    objs = models.LKLD1.objects.filter(terminal__in=pos_list)
    for obj in objs:
        if obj.card_type == u"贷记卡":
            month = obj.pay_date[:7]
            day = obj.pay_date[:10]
            if month <= "2018-01":
                continue
            # 100以下交易不计算
            if Decimal(obj.draw_rmb) < 100:
                continue
            trans_total += Decimal(obj.draw_rmb)
            if day > end_day:
                freeze_total += Decimal(obj.draw_rmb)
    return str(trans_total), str(freeze_total)


def get_user_txz_rmb(user):
    total = 0
    objs = models.TiXianOrder.objects.filter(user=user).filter(status="PD")
    for obj in objs:
        total += obj.rmb
    return total


def can_tixian(user):
    end = int(time.time())
    with transaction.atomic():
        objs = models.TiXianOrder.objects.select_for_update().filter(user=user).order_by("-create_time")
        if objs:
            obj = objs[0]
            status_wait = [o.status for o in objs if o.status != "SU"]
        else:
            obj = None
            status_wait = []
    if not obj:
        tx = True
    elif len(status_wait) > 0:
        return False
    else:
        start = utils.datetime_to_timestamp(obj.create_time)
        if end - start > 60:
            tx = True
        else:
            tx = False
    return tx


def _is_double_ok(open_date_str, terminal):
    open_date = string_to_datetime(open_date_str[:10], "%Y-%m-%d")
    end_date = open_date + timedelta(30)
    end_date_str = "{}-{:02}-{:02}".format(end_date.year, end_date.month, end_date.day)
    ok = False
    objs = models.LKLD1.objects.filter(terminal=terminal)
    trans_total = Decimal(0)
    for obj in objs:
        if obj.card_type == u"贷记卡":
            day = obj.pay_date[:10]
            if day < end_date_str:
                trans_total += Decimal(obj.draw_rmb)
        if trans_total > 20000:
            break
    if trans_total >= 20000:
        ok = True
    return ok


def get_terminal_status(terminal):
    """
    终端状态
    """
    objs = models.LKLTerminal.objects.filter(terminal=terminal)
    if objs:
        obj = objs[0]
        if obj.is_ok == u"是":
            s = u"达标"
            if _is_double_ok(obj.open_date, obj.terminal):
                s = u"双达标"
        else:
            s = u"未达标"
    else:
        s = u"未激活"
    return s


def set_user_fenrun(user, point, rmb):
    obj, created = models.UserFenRun.objects.update_or_create(
        user=user,
        defaults={'point': point, "rmb": rmb},
    )


def get_last_fenren_order(user, child):
    objs = models.FenRunOrder.objects.filter(user=user, child=child).order_by("-create_time")
    if objs:
        obj = objs[0]
    else:
        obj = None
    return obj


def get_user_pos_top():
    objs = models.UserPos.objects.all()
    user_dict = {}
    for obj in objs:
        if obj.user in user_dict:
            user_dict[obj.user] += 1
        else:
            user_dict[obj.user] = 1
    good_user = [(user, n) for user, n in user_dict.iteritems() if n >= 10]
    return sorted(good_user, key=lambda x: -x[1])


# token
def get_token_code():
    objs = models.SLKLToken.objects.filter(is_disabled=False).order_by("-create_time")
    if objs:
        token = objs[0].token
    else:
        token = None
    return token


def disable_token(token):
    objs = models.SLKLToken.objects.filter(token=token)
    for obj in objs:
        obj.is_disabled = True
        obj.save()


def add_token(token):
    obj = models.SLKLToken.objects.create(token=token)
    return obj


def del_token():
    now = datetime.now() - timedelta(1)
    objs = models.SLKLToken.objects.filter(create_time__lt=now)
    objs.delete()


# 微信绑定相关
def is_bing_wx(user):
    objs = models.WXUser.objects.filter(user=user)
    if objs:
        return True
    else:
        return False


def get_wx_user(user):
    objs = models.WXUser.objects.filter(user=user)
    if objs:
        return objs[0]
    else:
        return None


def get_wx_user_by_openid(openid):
    objs = models.WXUser.objects.filter(openid=openid)
    if objs:
        return objs[0]
    else:
        return None
