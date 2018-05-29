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


def get_client_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if ip:
        return ip.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', None)


def wx_tixian(open_id, fen, name, user_ip="139.199.102.27"):
    """
    {'partner_trade_no': '1498390922201805216403871295',
    'payment_time': '2018-05-21 21:03:15',
    'nonce_str': 'sMDj3abwf1y5zUhci6xDxDCiIVARFdqT',
    'return_code': 'SUCCESS',
    'mch_appid': 'wx3274fa5ad5bb8cbc',
    'payment_no': '1000018301201805217958360686',
    'mchid': '1498390922',
    'return_msg': None,
    'result_code': 'SUCCESS'}
    """
    from .wx_pay import WxPay
    pay = WxPay()
    api_cert_path = "/root/wxpay/apiclient_cert.pem"
    api_key_path = "/root/wxpay/apiclient_key.pem"
    data = {
        "openid": open_id,
        "amount": fen,
        "check_name": "FORCE_CHECK",
        "re_user_name": name,
        "spbill_create_ip": user_ip,
        "desc": u"分润发放"
    }
    res = pay.enterprise_payment(api_cert_path, api_key_path, **data)
    return res
