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

TAX = "0.91"  # 税点 9


class Command(BaseCommand):
    """
    推荐奖励
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
        print "__sync jk child user rmb", start_date, end_date
        print now
        default_user = get_user_by_username("13300000000")
        # SYFTrade
        used_trans_ids = set(models.JKChildProfit.objects.values_list("trans_id", flat=True))
        objs = models.JKProfit.objects.all()
        for obj in objs:
            if obj.trans_id in used_trans_ids:
                continue
            adatetime = utils.string_to_datetime(obj.trade_date[:10], format_str="%Y-%m-%d")
            adate = adatetime.date()
            if start_date <= adate <= end_date:
                process_jk_child_rmb(obj, default_user)
        print "ok"


def process_jk_child_rmb(obj, default_user):
    user = obj.user
    if hasattr(user, "userprofile"):
        father = user.userprofile.father
        if not father:
            print "no father! user", user.username
            return
        else:
            if hasattr(father, "jkfenrun"):
                fenrun_father_point = father.jkfenrun.point
            else:
                print "no father fenrun!!", father.username
                return
    else:
        print "no userprofile!", user.username
        return
    # 根据father的提点计算可得分润
    try:
        system_rmb = Decimal(obj.fenrun)
    except Exception:
        print "no system fenrun"
        return
    shua_point = Decimal(obj.trade_fee) / Decimal(obj.trade_rmb) * Decimal("100")
    shua_point = shua_point.quantize(Decimal('1.00'), ROUND_DOWN)
    diff_point = shua_point - Decimal(fenrun_father_point)
    if diff_point <= 0:
        xrmb = 0
        rmb = 0
    else:
        myrmb = Decimal(diff_point) / Decimal(shua_point) * Decimal(obj.trade_fee)
        myrmb = myrmb.quantize(Decimal('1.00'), ROUND_DOWN)
        if myrmb > system_rmb:
            print "user rmb bigger than system rmb!!!"
            print obj.trans_id
            return
        armb = myrmb * Decimal(TAX)  # 税点 9
        xrmb = armb.quantize(Decimal('1.00'), ROUND_DOWN)
        father_rmb = int(100 * Decimal(xrmb))
        rmb = father_rmb - obj.rmb
        rmb = max(0, rmb)
    profit = models.JKChildProfit.objects.create(
        user=user,
        father=father,
        trans_id=obj.trans_id,
        fenrun_point=obj.fenrun_point,
        fenrun_father_point=fenrun_father_point,
        child_rmb=obj.rmb,
        rmb=rmb,
        merchant_code=obj.merchant_code,
        terminal=obj.terminal,
        trade_date=obj.trade_date,
        trade_rmb=obj.trade_rmb,
        trade_status=obj.trade_status,
        return_code=obj.return_code,
        trade_fee=obj.trade_fee,
        card_type=obj.card_type,
        qingfen_rmb=obj.qingfen_rmb,
        fenrun=obj.fenrun,
        trade_category=obj.trade_category,
        product=obj.product
    )
    profit.status = "PD"
    profit.pay_time = datetime.now()
    profit.save()
    dbutils.add_jkuserrmb_child_rmb(father, profit.rmb)
    profit.status = "SU"
    profit.save()
    print "give father user jk profile ok", obj.trans_id, father.username, profit.rmb
