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
    分润申请短信通知
    """
    @wrapper_raven
    def handle(self, *args, **options):
        print "__start fr_msg..."
        print datetime.now()
        start_date = datetime.now() - timedelta(1)
        objs = models.FenRunOrder.objects.filter(status="WAIT").filter(create_time__gt=start_date)
        time_x = u"近一天"
        total = len(objs)
        if total > 0:
            template_id = 93509
            params = [time_x, total]
            send_tsms_multi(TX_MSG, template_id, params)
