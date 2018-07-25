# -*- coding: utf-8 -*-
import redis
import string
import random
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal, ROUND_DOWN
from django.conf import settings
from . import models
from . import dbutils
from jinkong.models import JKTerminal, JKTrade, JKUserRMB, JKTiXianOrder


def get_boss_pos_info():
    """
    获取全部用户达标机器数量
    """
    res_dict = {}
    objs = models.LKLTerminal.objects.all()
    for obj in objs:
        month = obj.open_date[:7]
        ok = int(obj.is_ok == u"是")
        if month not in res_dict:
            res_dict[month] = {
                "ok": ok,
                "total": 1
            }
        else:
            res_dict[month]["ok"] += ok
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


def get_reminder_data():
    """
    3月份开始，只有当月激活，当月刷2000才算合格
    """
    # d = datetime.now() - timedelta(29)
    # start = "{}-{:02}-{:02}".format(d.year, d.month, d.day)
    d = datetime.now()
    current_month = "{}-{:02}".format(d.year, d.month)
    objs = models.LKLTerminal.objects.filter(is_ok=u"否")
    data = []
    for obj in objs:
        month = obj.open_date[:7]
        if month != current_month:
            continue
        # day = obj.open_date[:10]
        # if day < start:
        #     continue
        user = dbutils.get_user_by_terminal(obj.terminal)
        if user:
            if hasattr(user, "userprofile"):
                name = user.userprofile.name
                phone = user.username
            else:
                name = u"未知"
                phone = u"未知"
        else:
            name = u"未被绑定"
            phone = u"未被绑定"
        info = {
            "name": name,
            "phone": phone,
            "terminal": obj.terminal,
            "open_date": obj.open_date
        }
        data.append(info)
    return data


# 金控相关
def get_jk_boss_pos_info():
    """
    获取全部用户达标机器数量
    """
    res_dict = {}
    objs = JKTerminal.objects.all()
    for obj in objs:
        month = obj.install_date[:7]
        ok = int(obj.fee_receive == u"是")
        if month not in res_dict:
            res_dict[month] = {
                "ok": ok,
                "total": 1
            }
        else:
            res_dict[month]["ok"] += ok
            res_dict[month]["total"] += 1
    return res_dict


def get_jk_boss_trade_info():
    """
    获取全部用户刷卡总额
    """
    res_dict = {}
    objs = JKTrade.objects.filter(card_type=u"贷记").filter(return_code="00")
    for obj in objs:
        month = obj.trade_date[:7]
        armb = Decimal("8") / Decimal("10000") * Decimal(obj.trade_rmb)
        armb = armb.quantize(Decimal('1.00'), ROUND_DOWN)
        fee = Decimal(obj.trade_fee)
        if fee > 0:
            rmb = armb - fee
        else:
            rmb = Decimal("0")
        if month not in res_dict:
            res_dict[month] = {
                "draw": Decimal(obj.trade_rmb),
                "fee": fee,
                "rmb": rmb
            }
        else:
            res_dict[month]["draw"] += Decimal(obj.trade_rmb)
            res_dict[month]["fee"] += fee
            res_dict[month]["rmb"] += rmb
    return res_dict


def get_jk_all_urmb():
    objs = JKUserRMB.objects.all()
    rmb = 0
    child_rmb = 0
    for obj in objs:
        rmb += obj.rmb
        child_rmb += obj.child_rmb
    return rmb, child_rmb


def get_jk_all_txrmb():
    objs = JKTiXianOrder.objects.all()
    total = 0
    for obj in objs:
        total += obj.rmb
    return total
