# -*- coding: utf-8 -*-
import sys
from decimal import Decimal, ROUND_DOWN
import warnings
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from user import models
from lkl import utils
from user.utils import get_user_by_username
from user import dbutils

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")


class Command(BaseCommand):
    """
    D0 分给用户 一个商户，多个终端，给默认用户
    D1 分给用户 100以下的不分，给默认用户
    D1 手续费/60*x 就是分给用户的
    起始结算日期为2018-02-01
    结算日期延迟3天，不含今天
    """
    def add_arguments(self, parser):
        parser.add_argument(
            '--start',
            action='store',
            dest='start',
            help=''
        )
        parser.add_argument(
            '--end',
            action='store',
            dest='end',
            help=''
        )
        parser.add_argument(
            '--table',
            action='store',
            dest='table',
            help=''
        )

    def handle(self, start, end, table, *args, **options):
        if end is None:
            end_datetime = datetime.now() - timedelta(4)
        else:
            end_datetime = utils.string_to_datetime(end, format_str="%Y-%m-%d")
        if start is None:
            start_datetime = end_datetime - timedelta(3)
        else:
            start_datetime = utils.string_to_datetime(start, format_str="%Y-%m-%d")
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        # start = utils.datetime_to_string(start_date, format_str="%Y-%m-%d")
        # end = utils.datetime_to_string(end_date, format_str="%Y-%m-%d")
        print "sync user rmb", start_date, end_date, table
        default_user = get_user_by_username("13300000000")
        # D0
        if table in ("d0", "all"):
            used_trans_ids = set(models.ProfitD0.objects.values_list("trans_id", flat=True))
            objs = models.LKLD0.objects.filter(fee_rmb="2").filter(trans_type=u"正交易").filter(trans_status=u"成功")
            for obj in objs:
                if obj.trans_id in used_trans_ids:
                    continue
                adatetime = utils.string_to_datetime(obj.draw_date, format_str="%Y%m%d %H:%M:%S")
                adate = adatetime.date()
                if start_date <= adate <= end_date:
                    process_d0_rmb(obj, default_user)
        # D1
        if table in ("d1", "all"):
            used_trans_ids = set(models.ProfitD1.objects.values_list("trans_id", flat=True))
            objs = models.LKLD1.objects.filter(card_type=u"贷记卡")
            for obj in objs:
                if obj.trans_id in used_trans_ids:
                    continue
                adatetime = utils.string_to_datetime(obj.pay_date, format_str="%Y-%m-%d %H:%M:%S.0")
                adate = adatetime.date()
                if start_date <= adate <= end_date:
                    process_d1_rmb(obj, default_user)


def process_d0_rmb(obj, default_user):
    user = dbutils.get_user_by_mcode(obj.merchant_code)
    if user is None:
        print "user is None!"
        return
    elif user == "multi":
        print "d0 default user..."
        user = default_user
    if hasattr(user, "userfenrun"):
        user_point = user.userfenrun.point
        user_rmb = user.userfenrun.rmb
    else:
        print "no user fenrun!"
        return
    profit = models.ProfitD0.objects.create(
        user=user,
        trans_id=obj.trans_id,
        fenrun_point=user_point,
        fenrun_rmb=user_rmb,
        rmb=int(100 * Decimal(user_rmb)),
        merchant_code=obj.merchant_code,
        draw_date=obj.draw_date,
        draw_rmb=obj.draw_rmb,
        fee_rmb=obj.fee_rmb,
        real_rmb=obj.real_rmb,
        trans_type=obj.trans_type,
        trans_status=obj.trans_status
    )
    profit.status = "PD"
    profit.pay_time = datetime.now()
    profit.save()
    dbutils.add_userrmb_rmb(user, profit.rmb)
    profit.status = "SU"
    profit.save()
    print "give user d0 profile ok", user.username, profit.rmb


def process_d1_rmb(obj, default_user):
    user = dbutils.get_user_by_terminal(obj.terminal)
    if user is None:
        print "user is None!"
        return
    elif Decimal(obj.draw_rmb) < 100:
        print "d1 default user..."
        user = default_user
    if hasattr(user, "userfenrun"):
        user_point = user.userfenrun.point
        user_rmb = user.userfenrun.rmb
    else:
        print "no user fenrun!"
        return
    armb = Decimal(user_point) / Decimal("60") * Decimal(obj.fee_rmb)
    xrmb = armb.quantize(Decimal('1.00'), ROUND_DOWN)
    profit = models.ProfitD1.objects.create(
        user=user,
        trans_id=obj.trans_id,
        fenrun_point=user_point,
        fenrun_rmb=user_rmb,
        rmb=int(100 * Decimal(xrmb)),
        merchant_code=obj.merchant_code,
        draw_date=obj.draw_date,
        draw_rmb=obj.draw_rmb,
        fee_rmb=obj.fee_rmb,
        card_type=obj.card_type,
        pay_date=obj.pay_date,
        terminal=obj.terminal
    )
    profit.status = "PD"
    profit.pay_time = datetime.now()
    profit.save()
    dbutils.add_userrmb_rmb(user, profit.rmb)
    profit.status = "SU"
    profit.save()
    print "give user d1 profile ok", user.username, profit.rmb
