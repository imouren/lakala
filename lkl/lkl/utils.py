# -*- coding: utf-8 -*-
from datetime import datetime


def datetime_to_string(adatetime, format_str="%Y%m%d"):
    return adatetime.strftime(format_str)


def string_to_datetime(time_str, format_str="%Y%m%d"):
    return datetime.strptime(time_str, format_str)
