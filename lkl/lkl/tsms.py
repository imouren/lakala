# -*- coding: utf-8 -*-
from qcloudsms_py import SmsSingleSender, SmsMultiSender
from .config import TSMS_APP_ID, TSMS_APP_KEY


def send_tsms_single(phone, template_id, params):
    ssender = SmsSingleSender(TSMS_APP_ID, TSMS_APP_KEY)
    try:
        ssender.send_with_param(86, phone, template_id, params)
    except Exception as e:
        print(e)


def send_tsms_multi(phones, template_id, params):
    msender = SmsMultiSender(TSMS_APP_ID, TSMS_APP_KEY)
    try:
        msender.send_with_param(86, phones, template_id, params)
    except Exception as e:
        print(e)
