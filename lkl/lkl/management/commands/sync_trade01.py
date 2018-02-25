# -*- coding: utf-8 -*-
import sys
import warnings
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO
import requests
from pytesseract import image_to_string
from django.core.management.base import BaseCommand
from lkl import utils, config
from user.models import LKLTrade01
from user.utils import wrapper_raven

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

URL = "https://mposa.lakala.com/queryTrade"
LOGIN_URL = "https://mposa.lakala.com/login"
IMG_URL = "https://mposa.lakala.com/generateValidateCode"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    'Content-type': 'application/x-www-form-urlencoded',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) C,hrome/43.0.2357.124 Safari/537.36",
}


class Command(BaseCommand):
    """
    同步视频对应主题到redis
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
        try:
            start_date = utils.string_to_datetime(start)
            end_date = utils.string_to_datetime(end)
            if end_date < start_date:
                end_date = start_date
        except Exception:
            end_date = datetime.now()
            start_date = end_date - timedelta(3)
        print "sync trade01", start_date, end_date
        diff = end_date - start_date
        # 登陆操作
        code = get_code_value()
        data = {
            "loginName": config.LKL_USER,
            "userPwd": config.LKL_PWD,
            "code": code
        }
        res = requests.post(LOGIN_URL, data, headers=HEADERS, verify=False)
        sid = res.json().get("retData", {}).get("sessionId")
        cookies = res.cookies
        if sid:
            for i in range(diff.days + 1):
                adate = start_date + timedelta(i)
                adate_str = utils.datetime_to_string(adate)
                print adate_str
                get_one_day_data(adate_str, sid, cookies)
        else:
            print res.json()["retMsg"]
        print "ok"


def get_one_day_data(date_str, sid, cookies):
    page = 1
    while True:
        data = {
            "type": "T_01",
            "pageSize": 10,
            "pageNo": page,
            "startDate": date_str,
            "endDate": date_str,
            "merchantExtCode": "",
            "merchantCode": "",
            "transCode": "P_ALL",
            "signOrg": "",
            "termNo": "",
            "sessionId": sid
        }
        res = requests.post(URL, data, headers=HEADERS, cookies=cookies, verify=False)
        result = res.json()
        if result["retCode"] != "SUCCESS":
            print result
            break
        ret = result["retData"]["content"]["resultModel"]
        rows = ret["rows"]
        write_to_db(date_str, rows)
        if len(rows) < 10:
            break
        page += 1


def write_to_db(date_str, data):
    # 原有数据
    tids = [trade["transId"] for trade in data]
    used_tids = set(LKLTrade01.objects.filter(transId__in=tids).values_list("transId", flat=True))
    # 插入db
    alist = []
    for trade in data:
        if trade["transId"] not in used_tids:
            obj = LKLTrade01(
                merchantCode=trade["merchantCode"],
                maintainOrg=trade["maintainOrg"],
                transId=trade["transId"],
                cardType=trade["cardType"],
                transCode=trade["transCode"],
                termNo=trade["termNo"],
                payAmt=trade["payAmt"],
                cardNo=trade["cardNo"],
                feeAmt=trade["feeAmt"],
                sid=trade["sid"],
                merchantName=trade["merchantName"],
                transType=trade["transType"],
                signimage=trade["signimage"],
                transAmt=trade["transAmt"],
                trade_date=date_str,
            )
            alist.append(obj)
    if alist:
        LKLTrade01.objects.bulk_create(alist)


def init_table(threshold=250):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table


def get_code_value(img_url=IMG_URL):
    response = requests.get(img_url, verify=False, headers=HEADERS)
    im = Image.open(BytesIO(response.content))
    im = im.convert('L')
    binary_image = im.point(init_table(250), '1')
    value = image_to_string(binary_image, config='-psm 7 chars')
    if len(value) == 5:
        return value
    else:
        return get_code_value(img_url)
