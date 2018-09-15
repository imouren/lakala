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
    objs = models.HHJKToken.objects.filter(is_disabled=False).order_by("-create_time")
    if objs:
        token = objs[0].token
    else:
        token = None
    return token


def disable_token(token):
    objs = models.HHJKToken.objects.filter(token=token)
    for obj in objs:
        obj.is_disabled = True
        obj.save()
    # send_token_msg()


def add_token(token):
    obj = models.HHJKToken.objects.create(token=token)
    return obj


def del_token():
    now = datetime.now() - timedelta(1)
    objs = models.HHJKToken.objects.filter(create_time__lt=now)
    objs.delete()


def get_terminal_by_sn_code(code):
    objs = models.HHJKTerminal.objects.filter(sn_code__endswith=code)
    if objs:
        obj = objs[0]
        return obj
    return None


def exists_merchant_phone(phone):
    objs = models.HHJKMerchant.objects.filter(phone=phone)
    if objs:
        return True
    else:
        return False


def get_merchant(merchant_code):
    objs = models.HHJKMerchant.objects.filter(merchant_code=merchant_code)
    if objs:
        obj = objs[0]
    else:
        obj = None
    return obj


def get_merchants_by_phone(phone):
    objs = models.HHJKMerchant.objects.filter(phone=phone)
    return objs
