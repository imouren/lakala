# -*- coding: utf-8 -*-
import string
import random
from decimal import Decimal
from django.contrib.auth.models import User
from .models import UserProfile, LKLTrade01


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
                data[month] = Decimal(0)
    trade_data = [(k, str(v)) for k, v in data.iteritems()]
    trade_data.sort()
    trade_data.append((u"小计", str(sum(data.values()))))
    return trade_data
