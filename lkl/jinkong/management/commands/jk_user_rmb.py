# -*- coding: utf-8 -*-
import sys
from decimal import Decimal, ROUND_DOWN
import warnings
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from jinkong import models
from lkl import utils
from user.utils import get_user_by_username, wrapper_raven
from jinkong import dbutils

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")


class Command(BaseCommand):
    """
    实时结算
    不结算300 220元的订单
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

    @wrapper_raven
    def handle(self, start, end, *args, **options):
        now = datetime.now()
        if end is None:
            end_datetime = now
        else:
            end_datetime = utils.string_to_datetime(end, format_str="%Y-%m-%d")
        if start is None:
            start_datetime = end_datetime - timedelta(3)
        else:
            start_datetime = utils.string_to_datetime(start, format_str="%Y-%m-%d")
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        print "__sync jk user rmb", start_date, end_date
        print now
        default_user = get_user_by_username("13300000000")
        # SYFTrade
        used_trans_ids = set(models.JKProfit.objects.values_list("trans_id", flat=True))
        objs = models.JKTrade.objects.filter(card_type=u"贷记").filter(return_code="00")
        # if obj.trade_card_type == u"贷记卡" and obj.return_code == "00" and obj.trade_rmb != "299.0":
        for obj in objs:
            if obj.trans_id in used_trans_ids:
                continue
            if obj.product.strip() == "" and obj.trade_category.strip() == "" and obj.trade_rmb != "220.0" and obj.trade_rmb != "300.0":
                adatetime = utils.string_to_datetime(obj.trade_date[:8], format_str="%Y%m%d")
                adate = adatetime.date()
                if start_date <= adate <= end_date:
                    process_jk_rmb(obj, default_user)
        print "ok"


def process_jk_rmb(obj, default_user):
    user = dbutils.get_user_by_terminal(obj.terminal)
    if user is None:
        print "user is None!"
        return

    if hasattr(user, "jkfenrun"):
        user_point = user.jkfenrun.point
    else:
        print "no user fenrun!"
        return
    try:
        system_rmb = Decimal(obj.fenrun)
    except Exception:
        print "no system fenrun"
        return
    shua_point = Decimal(obj.trade_fee) / Decimal(obj.trade_rmb) * Decimal("100")
    shua_point = shua_point.quantize(Decimal('1.00'), ROUND_DOWN)
    diff_point = shua_point - Decimal(user_point)
    if diff_point <= 0:
        xrmb = 0
    else:
        myrmb = Decimal(diff_point) / Decimal(user_point) * Decimal(obj.trade_fee)
        myrmb = myrmb.quantize(Decimal('1.00'), ROUND_DOWN)
        if myrmb > system_rmb:
            print "user rmb bigger than system rmb!!!"
            return
        armb = myrmb * Decimal("0.92")
        xrmb = armb.quantize(Decimal('1.00'), ROUND_DOWN)
    profit = models.JKProfit.objects.create(
        user=user,
        trans_id=obj.trans_id,
        fenrun_point=user_point,
        rmb=int(100 * Decimal(xrmb)),
        merchant_code=obj.merchant_code,
        terminal=obj.terminal,
        trade_date=obj.trade_date,
        trade_rmb=obj.trade_rmb,
        trade_status=obj.trade_status,
        return_code=obj.return_code,
        trade_fee=obj.trade_fee,
        card_type=obj.card_type,
        qingfen_rmb=obj.qingfen_rmb,
        trade_card_type=obj.trade_card_type,
        fenrun=obj.fenrun,
        trade_category=obj.trade_category,
        product=obj.product
    )
    profit.status = "PD"
    profit.pay_time = datetime.now()
    profit.save()
    dbutils.add_jkuserrmb_rmb(user, profit.rmb)
    profit.status = "SU"
    profit.save()
    print "give user jk profile ok", user.username, profit.rmb
