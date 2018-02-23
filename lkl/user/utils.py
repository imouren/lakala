# -*- coding: utf-8 -*-
import string
import random
from collections import defaultdict
from decimal import Decimal
from django.contrib.auth.models import User
from .models import UserProfile, LKLTrade01, UserPos, LKLD1


def get_user_by_code(code, is_phone):
    if is_phone:
        objs = UserProfile.objects.filter(phone=code)
    else:
        objs = UserProfile.objects.filter(code=code)
    if objs and len(objs) == 1:
        return objs[0].user
    else:
        return None


def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user


def exists_code(code):
    objs = UserProfile.objects.filter(code=code)
    if objs:
        return True
    else:
        return False


def _generate_code(n):
    res = []
    s = string.letters + string.digits
    for i in range(n):
        letter = random.choice(s)
        res.append(letter)
    return "".join(res)


def generate_code(n=6):
    code = _generate_code(n)
    if exists_code(code):
        return generate_code(n)
    else:
        return code


def get_trade_by_terminal(terminal):
    data = {}
    objs = LKLTrade01.objects.filter(termNo=terminal)
    for obj in objs:
        if obj.transType == u"刷卡":
            month = obj.trade_date[:6]
            if month in data:
                data[month] += Decimal(obj.feeAmt)
            else:
                data[month] = Decimal(obj.feeAmt)
    trade_data = [(k, str(v)) for k, v in data.iteritems()]
    trade_data.sort()
    trade_data.append((u"小计", str(sum(data.values()))))
    return trade_data


def get_trade_by_terminal2(terminal):
    data = defaultdict(list)
    objs = LKLTrade01.objects.filter(termNo=terminal)
    for obj in objs:
        if obj.transType == u"刷卡" and obj.cardType == u"贷记卡":
            month = obj.trade_date[:6]
            data[month].append([Decimal(obj.transAmt), Decimal(obj.feeAmt)])
    trade_data = []
    trans_total = Decimal(0)
    fee_total = Decimal(0)
    for m in data:
        trans, fee = zip(*data[m])
        trans_sum = sum(trans)
        fee_sum = sum(fee)
        trade_data.append([m, str(trans_sum), str(fee_sum)])
        trans_total += trans_sum
        fee_total += fee_sum
    trade_data.sort()
    trade_data.append([u"小计", str(trans_total), str(fee_total)])
    return trade_data


def get_d1_by_terminal(terminal):
    data = defaultdict(list)
    objs = LKLD1.objects.filter(terminal=terminal)
    for obj in objs:
        if obj.card_type == u"贷记卡":
            month = obj.pay_date[:7]
            if month == "2018-01":
                continue
            # 100以下交易不计算
            if Decimal(obj.draw_rmb) < 100:
                continue
            data[month].append([Decimal(obj.draw_rmb), Decimal(obj.fee_rmb)])
    trade_data = []
    trans_total = Decimal(0)
    fee_total = Decimal(0)
    for m in data:
        trans, fee = zip(*data[m])
        trans_sum = sum(trans)
        fee_sum = sum(fee)
        trade_data.append([m, str(trans_sum), str(fee_sum)])
        trans_total += trans_sum
        fee_total += fee_sum
    trade_data.sort()
    trade_data.append([u"小计", str(trans_total), str(fee_total)])
    return trade_data


def get_d1_by_terminal_together(terminal):
    """
    新老网站的数据汇总到一起
    """
    data = defaultdict(list)
    # 老系统数据
    dict_old = {}
    objs = LKLD1.objects.filter(terminal=terminal)
    for obj in objs:
        if obj.card_type == u"贷记卡":
            month_str = obj.pay_date[:7]
            month = "".join(month_str.split("-"))
            # 100以下交易不计算
            if Decimal(obj.draw_rmb) < 100:
                continue
            tmp = [month, Decimal(obj.draw_rmb), Decimal(obj.fee_rmb)]
            dict_old[obj.trans_id] = tmp
    # 新系统数据
    dict_new = {}
    objs = LKLTrade01.objects.filter(termNo=terminal)
    for obj in objs:
        if obj.transType == u"刷卡" and obj.cardType == u"贷记卡":
            month = obj.trade_date[:6]
            # 100以下交易不计算
            if Decimal(obj.transAmt) < 100:
                continue
            tmp = [month, Decimal(obj.transAmt), Decimal(obj.feeAmt)]
            dict_new[obj.transId] = tmp
    # 汇总一起
    dict_old.update(dict_new)
    for tid, tmp in dict_old.iteritems():
        month, rmb, fee = tmp
        data[month].append([rmb, fee])

    trade_data = []
    trans_total = Decimal(0)
    fee_total = Decimal(0)
    for m in data:
        trans, fee = zip(*data[m])
        trans_sum = sum(trans)
        fee_sum = sum(fee)
        trade_data.append([m, str(trans_sum), str(fee_sum)])
        trans_total += trans_sum
        fee_total += fee_sum
    trade_data.sort()
    trade_data.append([u"小计", str(trans_total), str(fee_total)])
    return trade_data


def exists_pos_code(code):
    objs = UserPos.objects.filter(code=code)
    if objs:
        return True
    else:
        return False


def get_user_poses(user):
    objs = UserPos.objects.filter(user=user)
    poses = [obj.code for obj in objs]
    return poses
