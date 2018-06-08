# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from . import models
from . import utils
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
