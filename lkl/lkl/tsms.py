# -*- coding: utf-8 -*-
from qcloudsms_py import SmsSingleSender
from .config import TSMS_APP_ID, TSMS_APP_KEY

TEMPLATE_ID = 83039


def send_tsms(phone, code):
    ssender = SmsSingleSender(TSMS_APP_ID, TSMS_APP_KEY)
    params = [code, ]
    try:
        result = ssender.send_with_param(86, phone, TEMPLATE_ID, params)
    except Exception as e:
        print(e)
        result = None
    return result
