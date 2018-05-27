# -*- coding: utf-8 -*-
import sys
from decimal import Decimal, ROUND_DOWN
import warnings
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from xyf import models
from lkl import utils
from user.utils import get_user_by_username, wrapper_raven
from xyf import dbutils

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")


class Command(BaseCommand):
    """
    实时结算
    不结算299.0元的订单
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
        print "__sync xyf user rmb", start_date, end_date
        print now
        default_user = get_user_by_username("13300000000")
        # SYFTrade
        used_trans_ids = set(models.XYFProfit.objects.values_list("trans_id", flat=True))
        objs = models.SYFTrade.objects.filter(trade_card_type=u"贷记卡").filter(return_code="00")
        # if obj.trade_card_type == u"贷记卡" and obj.return_code == "00" and obj.trade_rmb != "299.0":
        for obj in objs:
            if obj.trans_id in used_trans_ids:
                continue
            adatetime = utils.string_to_datetime(obj.trade_date[:8], format_str="%Y%m%d")
            adate = adatetime.date()
            if start_date <= adate <= end_date:
                process_xyf_rmb(obj, default_user)
        print "ok"


def process_xyf_rmb(obj, default_user):
    user = dbutils.get_user_by_terminal(obj.terminal)
    if user is None:
        print "user is None!"
        return
    elif Decimal(obj.trade_rmb) == 299:
        print "rmb 299!"
        return

    if hasattr(user, "xyffenrun"):
        user_point = user.xyffenrun.point
    else:
        print "no user fenrun!"
        return
    armb = (Decimal("0.550") - Decimal(user_point)) / Decimal("0.55") * Decimal(obj.trade_fee) * Decimal("0.92")
    xrmb = armb.quantize(Decimal('1.00'), ROUND_DOWN)
    profit = models.XYFProfit.objects.create(
        user=user,
        trans_id=obj.trans_id,
        fenrun_point=user_point,
        rmb=int(100 * Decimal(xrmb)),
        terminal=obj.terminal,
        trade_date=obj.trade_date,
        trade_rmb=obj.trade_rmb,
        trade_fee=obj.trade_fee,
        trade_status=obj.trade_status,
        trade_card_type=obj.trade_card_type,
        return_code=obj.return_code
    )
    profit.status = "PD"
    profit.pay_time = datetime.now()
    profit.save()
    dbutils.add_xyfuserrmb_rmb(user, profit.rmb)
    profit.status = "SU"
    profit.save()
    print "give user xyf profile ok", user.username, profit.rmb
