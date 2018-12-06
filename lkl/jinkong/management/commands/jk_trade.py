# -*- coding: utf-8 -*-
import sys
import re
import warnings
from datetime import datetime, timedelta
import requests
from django.core.management.base import BaseCommand
from lkl import utils, config
from bs4 import BeautifulSoup
import time
from jinkong.models import JKTrade
from user.utils import wrapper_raven
from jinkong.dbutils import get_token_code, disable_token


reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

TIMEOUT = 120  # 超时时间
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
token = get_token_code()


class Command(BaseCommand):
    """
    数据来源http://119.18.194.36/
    终端设备管理--终端设备查询
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
        print "__jk terminal"
        if not token:
            print "no token!!"
            return
        date_list = []
        if not start or not end:
            end_date = datetime.now()
            for i in range(3):
                adate = end_date - timedelta(i)
                date_list.append(adate)
        else:
            start_date = utils.string_to_datetime(start)
            end_date = utils.string_to_datetime(end)
            date_list.append(start_date)
            n = 1
            while True:
                day_date = start_date + timedelta(n)
                date_list.append(day_date)
                n += 1
                if day_date >= end_date:
                    break
        cookies = get_cookies(token)
        for adate in date_list:
            adate_str = utils.datetime_to_string(adate, format_str="%Y-%m-%d")
            terminal_data = get_trade_data(cookies, adate_str)
            write_to_db_trade(terminal_data)
        print "ok"


def r1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)


def get_cookies(cookie_string):
    cookies = {}
    for cookie in cookie_string.split(";"):
        cookie = cookie.strip()
        k, v = cookie.split("=", 1)
        cookies[k] = v
    return cookies


def get_activate_trade(cookies, page, adate):
    url = "http://119.18.194.36/miniIfTrade/listMiniPosList"
    data = {
        "pageSize": "20",
        "pageNum": page,
        "flg": "1",
        "mercSn": "",
        "mercCnm": "",
        "mb_no": "",
        "trmNo": "",
        "dateStart": adate,
        "orgNo": "",
        "stlSts": "",
        "tranSts": "",
        "tradeType": "",
        "tranType": "",
        "productIden": "",
        "countProfit": "01",
    }
    r = requests.post(url, data=data, cookies=cookies)
    html = r.content.decode("utf-8")
    soup = BeautifulSoup(html)
    data = []
    total = r1(ur"var total                   = (\d+);", html)

    print "total", total, "page", page
    if not total or not total.isdigit():
        disable_token(token)
    else:
        total = int(total)
    tbody = soup.find("tbody")
    if tbody:
        for line in tbody.find_all("tr"):
            tmp = []
            for td in line.find_all("td"):
                tmp.append(td.text.strip())
            data.append(tmp)
    return data, total


def get_trade_data(cookies, adate):
    print "get_trade_data...", adate
    all_data = []
    page = 1
    retry = 3
    while True:
        try:
            data, total = get_activate_trade(cookies, page, adate)
        except Exception, e:
            print e
            retry -= 1
            if retry < 0:
                break
            else:
                continue
        all_data.extend(data)
        if page * 20 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db_trade(data):
    tids = [terminal[18] for terminal in data]
    used_tids = set(JKTrade.objects.filter(trans_id__in=tids).values_list("trans_id", flat=True))
    # 插入db
    alist = []
    same_code = set()
    for t in data:
        trans_id = t[18]
        if trans_id in same_code:
            print "same code", trans_id
            continue
        else:
            same_code.add(trans_id)
        if trans_id not in used_tids:
            obj = JKTrade(
                merchant_code=t[0],
                register_name=t[1],
                agent_name=t[2],
                phone=t[3],
                terminal=t[4],
                trade_date=t[5],
                trade_time=t[6],
                trade_rmb=t[7],
                trade_type=t[8],
                trade_status=t[9],
                is_miao=t[10],
                return_code=t[11],
                card_type=t[12],
                card_code=t[13],
                card_bank=t[14],
                trade_fee=t[15],
                trade_fj_fee=t[16],
                qingfen_rmb=t[17],
                trans_id=t[18],
                fenrun=t[19],
                trade_category=t[20],
                product=t[21],
            )
            alist.append(obj)
        else:
            itmes = JKTrade.objects.filter(trans_id=t[18])
            if itmes:
                item = itmes[0]
                item.merchant_code = t[0]
                item.register_name = t[1]
                item.agent_name = t[2]
                item.phone = t[3]
                item.terminal = t[4]
                item.trade_date = t[5]
                item.trade_time = t[6]
                item.trade_rmb = t[7]
                item.trade_type = t[8]
                item.trade_status = t[9]
                item.is_miao = t[10]
                item.return_code = t[11]
                item.card_type = t[12]
                item.card_code = t[13]
                item.card_bank = t[14]
                item.trade_fee = t[15]
                item.trade_fj_fee = t[16]
                item.qingfen_rmb = t[17]
                item.trans_id = t[18]
                item.fenrun = t[19]
                item.trade_category = t[20]
                item.product = t[21]
                item.save()
    if alist:
        JKTrade.objects.bulk_create(alist)
