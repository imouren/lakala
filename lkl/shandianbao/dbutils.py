# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from . import models


def get_token_code():
    objs = models.SDBToken.objects.filter(is_disabled=False).order_by("-create_time")
    if objs:
        token = objs[0].token
    else:
        token = None
    return token


def disable_token(token):
    objs = models.SDBToken.objects.filter(token=token)
    for obj in objs:
        obj.is_disabled = True
        obj.save()


def add_token(token):
    obj = models.SDBToken.objects.create(token=token)
    return obj


def del_token():
    now = datetime.now() - timedelta(1)
    objs = models.SDBToken.objects.filter(create_time__lt=now)
    objs.delete()
