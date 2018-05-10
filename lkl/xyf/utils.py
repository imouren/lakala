# -*- coding: utf-8 -*-
from lkl.tsms import send_tsms_multi
from lkl.config import XYF_TOKEN_MSG


def send_token_msg():
    template_id = 119811
    params = []
    send_tsms_multi(XYF_TOKEN_MSG, template_id, params)
