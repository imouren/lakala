# -*- coding: utf-8 -*-
import redis
from datetime import datetime
import random
import string
from lkl import config

rclient = redis.Redis(**config.REDIS_DATA)


def datetime_to_string(adatetime, format_str="%Y%m%d"):
    return adatetime.strftime(format_str)


def string_to_datetime(time_str, format_str="%Y%m%d"):
    return datetime.strptime(time_str, format_str)


def get_salt(n=4):
    res = [random.choice(string.digits) for i in range(n)]
    return "".join(res)
