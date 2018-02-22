# -*- coding: utf-8 -*-
import time
from django.db import transaction
from . import models


def add_userrmb_rmb(user, rmb):
    with transaction.atomic():
        obj, created = models.UserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        obj.rmb += rmb
        obj.save()


def sub_userrmb_rmb(user, rmb):
    with transaction.atomic():
        obj, created = models.UserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
        obj.rmb -= rmb
        obj.save()


def get_userrmb_num(user):
    with transaction.atomic():
        obj, created = models.UserRMB.objects.select_for_update().get_or_create(user=user, defaults={"rmb": 0})
    return obj.rmb


def get_user_by_terminal(terminal):
    """
    通过终端号获取用户
    """
    try:
        obj = models.UserPos.get(code=terminal)
        user = obj.user
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
