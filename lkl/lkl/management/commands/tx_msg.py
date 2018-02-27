# -*- coding: utf-8 -*-
import sys
from decimal import Decimal, ROUND_DOWN
import warnings
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from user import models
from lkl import utils
from user.utils import get_user_by_username, wrapper_raven
from user import dbutils
from lkl.tsms import send_tsms_multi
from lkl.config import TX_MSG

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")


class Command(BaseCommand):
    """
    提现申请短信通知
    """
    @wrapper_raven
    def handle(self, *args, **options):
        print "__start tx_msg..."
        print datetime.now()
        objs = models.TiXianOrder.objects.filter(status="PD")
        names = []
        total = 0
        for obj in objs:
            if hasattr(obj.user, "userprofile"):
                name = obj.user.userprofile.name
            else:
                name = obj.user.username
            names.append(name)
            total += obj.rmb
        rmb = "%.2f" % (total / 100.0)
        if len(names) < 1:
            print "no user"
        elif len(names) > 3:
            template_id = 89726
            params = [u"所有", str(len(names)), rmb]
            send_tsms_multi(TX_MSG, template_id, params)
        else:
            template_id = 89712
            users = ",".join(names)
            params = [users, rmb]
            send_tsms_multi(TX_MSG, template_id, params)
        print "%s user %s rmb" % (len(names), rmb)
