# -*- coding: utf-8 -*-
import redis
import string
import random
import time
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN
from django.conf import settings
from . import models


def get_boss_pos_info():
    """
    获取全部用户达标机器数量
    """
    res_dict = {}
    objs = models.LKLTerminal.objects.all()
    for obj in objs:
        if obj.is_ok == u"是":
            month = obj.open_date[:7]
            if month not in res_dict:
                res_dict[month] = {
                    "ok": 1,
                    "total": 1
                }
            else:
                res_dict[month]["ok"] += 1
                res_dict[month]["total"] += 1
    return res_dict


def get_boss_d1_info():
    """
    获取全部用户D1刷卡总额
    """
    res_dict = {}
    objs = models.LKLD1.objects.all()
    for obj in objs:
        if obj.card_type == u"贷记卡":
            month = obj.pay_date[:7]
            if month == "2018-01":
                continue
            armb = Decimal("10") / Decimal("60") * Decimal(obj.fee_rmb)
            rmb = armb.quantize(Decimal('1.00'), ROUND_DOWN)
            if month not in res_dict:
                res_dict[month] = {
                    "draw": Decimal(obj.draw_rmb),
                    "fee": Decimal(obj.fee_rmb),
                    "rmb": rmb
                }
            else:
                res_dict[month]["draw"] += Decimal(obj.draw_rmb)
                res_dict[month]["fee"] += Decimal(obj.fee_rmb)
                res_dict[month]["rmb"] += rmb
    return res_dict


def get_boss_d0_info():
    """
    获取全部用户D0刷卡
    """
    res_dict = {}
    objs = models.LKLD0.objects.filter(fee_rmb="2").filter(trans_type=u"正交易").filter(trans_status=u"成功")
    for obj in objs:
        month = obj.draw_date[:6]
        if month == "201801":
            continue
        if month not in res_dict:
            res_dict[month] = {
                "n": 1,
                "rmb": 1.5
            }
        else:
            res_dict[month]["n"] += 1
            res_dict[month]["rmb"] += 1.5
    return res_dict


def get_all_urmb():
    objs = models.UserRMB.objects.all()
    rmb = 0
    child_rmb = 0
    for obj in objs:
        rmb += obj.rmb
        child_rmb += obj.child_rmb
    return rmb, child_rmb


def get_all_txrmb():
    objs = models.TiXianOrder.objects.all()
    total = 0
    for obj in objs:
        total += obj.rmb
    return total
