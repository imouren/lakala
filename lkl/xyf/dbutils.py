# -*- coding: utf-8 -*-
import time
from datetime import datetime, timedelta
from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from . import models
from . import utils
from lkl.utils import string_to_datetime


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


def add_token(token):
    obj = models.XYFToken.objects.create(token=token)
    return obj


def del_token():
    now = datetime.now() - timedelta(1)
    objs = models.XYFToken.objects.filter(create_time__lt=now)
    objs.delete()
