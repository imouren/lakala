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
from shandianbao.models import SDBTrade
from user.utils import wrapper_raven
from shandianbao.dbutils import get_token_code, disable_token


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
    'Host': 'shandianbao.chinapnr.com',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) C,hrome/43.0.2357.124 Safari/537.36",
}
DAYS = 1
token = get_token_code()


class Command(BaseCommand):
    """
    数据来源https://shandianbao.chinapnr.com/supm/TRD101/index
    交易管理---交易明细管理
    POST https://shandianbao.chinapnr.com/supm/TRD101/controlagent
    agentLevel=&merId=&agentId=&mobileId=&ordId=&payCardId=&transType=&transStat=&devsId=&dcType=&startDate=2018-08-30&endDate=2018-08-30&vipGate=
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
        print "__sdb trade"
        if not token:
            print "no token!!"
            return
        date_list = []
        if not start or not end:
            end_date = datetime.now()
            days = DAYS
            if end_date.hour < 10:
                days += 1
            for i in range(DAYS):
                adate = end_date - timedelta(i)
                date_list.append(adate)
        else:
            start_date = utils.string_to_datetime(start)
            end_date = utils.string_to_datetime(end)
            date_list.append(start_date)
            n = 1
            while True:
                day_date = start_date + timedelta(n)
                if day_date >= end_date:
                    break
                date_list.append(day_date)
                n += 1
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
    url = "https://shandianbao.chinapnr.com/supm/TRD101/controlagent"
    data = {
        "pageIndex": page,
        "agentId": "",
        "agentLevel": "",
        "mobileId": "",
        "ordId": "",
        "payCardId": "",
        "startDate": adate,
        "endDate": adate,
        "transType": "",
        "transStat": "",
        "devsId": "",
        "merId": "",
        "vipGate": "",
        "dcType": "",
    }
    r = requests.post(url, data=data, cookies=cookies)
    html = r.content.decode("utf-8")
    soup = BeautifulSoup(html)
    data = []
    total = r1(ur"共(\d+)条记录", html)
    # print html
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
        if page * 30 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db_trade(data):
    pk_index = 1
    tids = [terminal[pk_index] for terminal in data]
    used_tids = set(SDBTrade.objects.filter(trans_id__in=tids).values_list("trans_id", flat=True))
    # 插入db
    alist = []
    same_code = set()
    for t in data:
        trans_id = t[pk_index]
        if trans_id in same_code:
            print "same code", trans_id
            continue
        else:
            same_code.add(trans_id)
        if trans_id not in used_tids:
            obj = SDBTrade(
                trans_id=t[1],
                merchant=t[2],
                trade_date=t[3],
                trade_rmb=t[4],
                trade_type=t[5],
                trade_status=t[6],
                card_code=t[7],
                card_type=t[8],
                return_code=t[9],
                return_desc=t[10],
                terminal=t[11],
                agent_level=t[12],
                agent=t[13],
                business_type=t[14],
            )
            alist.append(obj)
        else:
            itmes = SDBTrade.objects.filter(trans_id=t[pk_index])
            if itmes:
                item = itmes[0]
                item.trans_id = t[1]
                item.merchant = t[2]
                item.trade_date = t[3]
                item.trade_rmb = t[4]
                item.trade_type = t[5]
                item.trade_status = t[6]
                item.card_code = t[7]
                item.card_type = t[8]
                item.return_code = t[9]
                item.return_desc = t[10]
                item.terminal = t[11]
                item.agent_level = t[12]
                item.agent = t[13]
                item.business_type = t[14]
                item.save()
    if alist:
        SDBTrade.objects.bulk_create(alist)
