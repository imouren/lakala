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

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")


DATA = [
    (datetime(2019, 6, 15), u"凝胶凉席"),
    (datetime(2019, 6, 30), u"风扇"),
    (datetime(2019, 6, 30), u"3d凉席"),
    (datetime(2019, 6, 29), u"安全座椅胸扣"),
    (datetime(2019, 6, 26), u"雨罩"),
    (datetime(2019, 6, 23), u"睡袋"),
    (datetime(2019, 6, 22), u"遮阳蓬"),
    (datetime(2019, 6, 21), u"爱婴居睡袋"),
    (datetime(2019, 6, 19), u"遮阳帘"),
    (datetime(2019, 6, 17), u"3D床垫"),
    (datetime(2019, 6, 13), u"防磨垫"),
    (datetime(2019, 6, 12), u"蚊帐"),
    (datetime(2019, 6, 11), u"置物袋"),
    (datetime(2019, 6, 8), u"车贴"),
    (datetime(2019, 6, 7), u"手套"),
    (datetime(2019, 6, 5), u"遮阳伞"),
]

TX_MSG = ["13121715957", "15001179460"]


class Command(BaseCommand):
    """
    提现申请短信通知
    """
    @wrapper_raven
    def handle(self, *args, **options):
        print "__start meizhe_msg..."
        start = datetime.now() + timedelta(2)
        for adate, txt in DATA:
            if adate > start:
                continue
            template_id = 334492
            params = [txt]
            send_tsms_multi(TX_MSG, template_id, params)
        print "ok"
