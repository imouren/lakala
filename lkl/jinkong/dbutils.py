# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from . import models
from lkl.utils import string_to_datetime


def get_token_code():
    objs = models.JKToken.objects.filter(is_disabled=False).order_by("-create_time")
    if objs:
        token = objs[0].token
    else:
        token = None
    return token


def disable_token(token):
    objs = models.JKToken.objects.filter(token=token)
    for obj in objs:
        obj.is_disabled = True
        obj.save()
    # send_token_msg()


def add_token(token):
    obj = models.JKToken.objects.create(token=token)
    return obj


def del_token():
    now = datetime.now() - timedelta(1)
    objs = models.JKToken.objects.filter(create_time__lt=now)
    objs.delete()


######################
def get_user_poses(user):
    objs = models.JKPos.objects.filter(user=user)
    poses = [(obj.sn_code, obj.terminal) for obj in objs if obj.terminal]
    return poses


def get_terminal_status(terminal):
    """
    终端状态
    """
    objs = models.JKTerminal.objects.filter(terminal=terminal)
    if objs:
        s = u"已激活"
    else:
        s = u"未激活"
    return s


def get_pos_status_num(poses):
    terminals = [pos[1] for pos in poses]
    objs = models.JKTerminal.objects.filter(terminal__in=terminals)
    dabiao = 0
    for obj in objs:
        if obj.fee_receive == u"是":
            dabiao += 1
    return len(objs), dabiao


def get_pos_detail(pos):
    detail = []
    objs = models.JKTrade.objects.filter(terminal=pos)
    trans_total = Decimal(0)
    fee_total = Decimal(0)
    for obj in objs:
        if obj.card_type == u"贷记" and obj.return_code == "00" and obj.product.strip() == "" and obj.trade_category.strip() == "" and obj.trade_rmb != "220.0" and obj.trade_rmb != "300.0":
            trans_total += Decimal(obj.trade_rmb)
            fee_total += Decimal(obj.trade_fee)
            tmp = {
                "draw_rmb": obj.trade_rmb,
                "fee_rmb": obj.trade_fee,
                "pay_date": obj.trade_date
            }
            detail.append(tmp)
    if detail:
        total = {
            "draw_rmb": trans_total,
            "fee_rmb": fee_total,
            "pay_date": u"总计"
        }
        detail.append(total)
    return detail


def get_user_trans_total(user):
    poses = get_user_poses(user)
    terminals = [pos[1] for pos in poses]
    objs = models.JKTrade.objects.filter(terminal__in=terminals)
    trans_total = Decimal(0)
    for obj in objs:
        if obj.card_type == u"贷记" and obj.return_code == "00" and obj.product.strip() == "" and obj.trade_category.strip() == "" and obj.trade_rmb != "220.0" and obj.trade_rmb != "300.0":
            trans_total += Decimal(obj.trade_rmb)
    return trans_total


def get_user_merchants(user):
    terminals = set(models.JKPos.objects.filter(user=user).values_list("terminal", flat=True))
    merchants = list(models.JKTerminal.objects.filter(terminal__in=terminals).values_list("merchant_code", flat=True))
    return merchants


# rmb operation
def add_jkuserrmb_rmb(user, rmb):
    with transaction.atomic():
        obj, created = models.JKUserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        obj.rmb += rmb
        obj.save()


def sub_jkuserrmb_rmb(user, rmb):
    with transaction.atomic():
        obj, created = models.JKUserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        obj.rmb -= rmb
        obj.save()


def get_jkuserrmb_num(user):
    with transaction.atomic():
        obj, created = models.JKUserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
    return obj.rmb


# child rmb operation
def add_jkuserrmb_child_rmb(user, rmb):
    with transaction.atomic():
        obj, created = models.JKUserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        obj.child_rmb += rmb
        obj.save()


def sub_jkuserrmb_child_rmb(user, rmb):
    with transaction.atomic():
        obj, created = models.JKUserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        obj.child_rmb -= rmb
        obj.save()


def get_jkuserrmb_child_num(user):
    with transaction.atomic():
        obj, created = models.JKUserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
    return obj.child_rmb


def get_jktxrmb_num(user):
    qs = models.JKTiXianOrder.objects.filter(user=user).filter(status="SU")
    total_rmb = qs.aggregate(Sum('rmb'))["rmb__sum"]
    if not total_rmb:
        total_rmb = 0
    return total_rmb


def get_user_by_terminal(terminal):
    """
    通过终端号获取用户
    """
    try:
        obj = models.JKPos.objects.get(terminal=terminal)
        user = obj.user
    except Exception:
        user = None
    return user


def get_terminal_by_sn_code(code):
    objs = models.JKTerminal.objects.filter(sn_code__endswith=code)
    if objs:
        obj = objs[0]
        return obj
    return None


def exists_pos_sn_code(code):
    objs = models.JKPos.objects.filter(sn_code=code)
    if objs:
        return True
    else:
        return False


def exists_merchant_phone(phone):
    objs = models.JKMerchant.objects.filter(phone=phone)
    if objs:
        return True
    else:
        return False
