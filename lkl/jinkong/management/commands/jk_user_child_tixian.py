# -*- coding: utf-8 -*-
import sys
import warnings
from datetime import datetime
from django.core.management.base import BaseCommand
from jinkong import models
from lkl.utils import wx_tixian
from user.utils import get_user_by_username, wrapper_raven
from user.dbutils import get_wx_user
from jinkong import dbutils


reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

MIN_RMB = 1000  # 10元起
FEE = 0.01  # 1%的手续费


class Command(BaseCommand):
    """
    实时结算
    不结算299.0元的订单
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--phone',
            action='store',
            dest='phone',
            help=''
        )

    @wrapper_raven
    def handle(self, phone, *args, **options):
        now = datetime.now()
        print "__sync jk user tixian"
        print now
        if phone == "all":
            objs = models.JKUserRMB.objects.filter(is_auto=True)
            tixian(objs)
        else:
            user = get_user_by_username(phone)
            if not user:
                print "no user", phone
                return
            if hasattr(user, "jkuserrmb"):
                objs = [user.jkuserrmb]
                tixian(objs)
        print "ok"


def tixian(objs):
    for obj in objs:
        print "start:", obj.user, obj.child_rmb
        user = obj.user
        user_rmb = obj.child_rmb
        if user_rmb < MIN_RMB:
            print "less than 10 RMB!"
            continue
        wx_user = get_wx_user(user)
        if not wx_user:
            print "no wx user!"
            continue
        if not hasattr(user, "userprofile"):
            print "no userprofile!"
            continue
        name = user.userprofile.name
        n = user_rmb / MIN_RMB
        tixian_rmb = n * MIN_RMB
        fee_rmb = int(tixian_rmb * FEE)
        real_rmb = tixian_rmb - fee_rmb
        tx = models.JKTiXianOrder.objects.create(
            user=user,
            user_account=wx_user.openid,
            rmb=tixian_rmb,
            fee=fee_rmb,
            order_type="CHILD_RMB",
        )
        dbutils.sub_jkuserrmb_child_rmb(user, tx.rmb)
        tx.pay_time = datetime.now()
        tx.status = "PD"
        tx.save()
        # give user wx rmb
        res = wx_tixian(wx_user.openid, str(real_rmb), name)
        if res["result_code"] == "SUCCESS":
            tx.status = 'SU'
            tx.finish_time = datetime.now()
            tx.save()
            print "pay ok!"
        else:
            print "pay error!"
            print res
