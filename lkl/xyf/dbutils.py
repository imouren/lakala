# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from . import models
from . import utils
from lkl.utils import string_to_datetime
from xyf.utils import send_token_msg


# token
def get_token_code():
    objs = models.XYFToken.objects.filter(is_disabled=False).order_by("-create_time")
    if objs:
        token = objs[0].token
    else:
        token = None
    return token


def disable_token(token):
    objs = models.XYFToken.objects.filter(token=token)
    for obj in objs:
        obj.is_disabled = True
        obj.save()
    send_token_msg()


def add_token(token):
    obj = models.XYFToken.objects.create(token=token)
    return obj


def del_token():
    now = datetime.now() - timedelta(1)
    objs = models.XYFToken.objects.filter(create_time__lt=now)
    objs.delete()


def get_user_poses(user):
    objs = models.XYFPos.objects.filter(user=user)
    poses = [(obj.sn_code, obj.terminal) for obj in objs if obj.terminal]
    return poses


def get_terminal_status(terminal):
    """
    终端状态
    """
    objs = models.SYFTerminal.objects.filter(terminal=terminal)
    if objs:
        obj = objs[0]
        if obj.ok_status == u"已达标":
            s = obj.ok_status
        else:
            s = obj.recharge_status
    else:
        s = u"未激活"
    return s


def get_pos_detail(pos):
    detail = []
    objs = models.SYFTrade.objects.filter(terminal=pos)
    trans_total = Decimal(0)
    fee_total = Decimal(0)
    for obj in objs:
        if obj.trade_card_type == u"贷记卡" and obj.return_code == "00":
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
    objs = models.SYFTrade.objects.filter(terminal__in=terminals)
    trans_total = Decimal(0)
    for obj in objs:
        if obj.trade_card_type == u"贷记卡" and obj.return_code == "00":
            trans_total += Decimal(obj.trade_rmb)
    return trans_total
