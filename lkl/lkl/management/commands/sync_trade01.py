# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from optparse import make_option
from lkl import utils, config
from PIL import Image
from io import BytesIO
import requests
from pytesseract import image_to_string

from django.core.management.base import BaseCommand

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
    option_list = BaseCommand.option_list + (
        make_option(
            '--start',
            action='store',
            dest='start',
            help=''),
        make_option(
            '--end',
            action='store',
            dest='end',
            help=''),
    )

    def handle(self, start, end, *args, **options):
        try:
            start_date = utils.string_to_datetime(start)
            end_date = utils.string_to_datetime(end)
            if end_date < start_date:
                end_date = start_date
        except Exception:
            start_date = end_date = datetime.now()
        diff = end_date - start_date
        # 登陆操作
        code = get_code_value()
        data = {
            "loginName": config.LKL_USER,
            "userPwd": config.LKL_PWD,
            "code": code
        }
        res = requests.post(LOGIN_URL, data, headers=HEADERS)
        sid = res.json().get("sessionId")
        cookies = res.cookies

        for i in (diff.days + 1):
            adate = start_date + timedelta(i)
            adate_str = utils.datetime_to_string(adate)
            print adate_str
            get_one_day_data(adate_str, sid, cookies)
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
        res = requests.post(URL, data, headers=HEADERS, cookies=cookies)
        result = res.json()
        if result["retCode"] != "SUCCESS":
            print result
            break
        ret = result["retData"]["content"]["resultModel"]
        if ret["nextPage"] == page or ret["lastPage"] == page:
            break
        else:
            rows = ret["rows"]
            write_to_db(rows)


def write_to_db(data):
    print data


def init_table(threshold=250):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table


def get_code_value(img_url=IMG_URL):
    response = requests.get(img_url)
    im = Image.open(BytesIO(response.content))
    im = im.convert('L')
    binary_image = im.point(init_table(250), '1')
    value = image_to_string(binary_image, config='-psm 7 chars')
    if len(value) == 5:
        return value
    else:
        return get_code_value(img_url)
