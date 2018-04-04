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
from xyf.models import SYFTrade
from user.utils import wrapper_raven
from xyf.dbutils import get_token_code, disable_token


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
    交易管理--当日交易明细
    """

    @wrapper_raven
    def handle(self, *args, **options):
        print "__xyf trade today"
        if not token:
            print "no token!!"
            return
        cookies = get_cookies(token)
        data = get_data(cookies)
        write_to_db(data)


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


def get_trade_today(cookies, page):
    url = "http://sddl.postar.cn/transaction_postxnjnl_day_query.trans"
    data = {
        "OPERATING": "stlw/query_txnjnl_agent_day.jsp",
        "pageNum": "%s" % page,
        "numPerPage": "12",
        "showFlag": "",
        "XYHeight": "",
        "FLAG": "2",
        "SUMTOAL": "",
        "AGTORG_1": "",
        "MERCNUM_1": "",
        "TXNCD_1": "",
        "TXNSTS_1": "",
        "LOGNO_1": "",
        "OPERSTATUS": "",
        "STATUS": "",
        "MERNAM_1": "",
        "TERMID": "",
        "TXNAMTSTR": "",
        "TXNAMTEND": "",
        "MERCID": "",
        "AGENTID": "",
        "merstlmod": "",
        "POStype": "",
        "SECPAYFLG": "",
        "PAYSTATUS": "",
        "ROTFLG1": "",
    }
    r = requests.post(url, data=data, cookies=cookies)
    html = r.content.decode("utf-8")
    soup = BeautifulSoup(html)
    data = []
    total = r1(ur"共\[(\d+)\]条", html)

    print "total", total, "page", page
    if not total or not total.isdigit():
        disable_token(token)
    else:
        total = int(total)
    content = soup.find("div", class_="pageContent")
    tbody = content.find("tbody")
    if tbody:
        for line in tbody.find_all("tr"):
            tmp = []
            for td in line.find_all("td"):
                tmp.append(td.text.strip())
            data.append(tmp)
    return data, total


def get_data(cookies):
    print "get_trade_data..."
    all_data = []
    page = 1
    retry = 3
    while True:
        try:
            data, total = get_trade_today(cookies, page)
        except Exception, e:
            print e
            retry -= 1
            if retry < 0:
                break
            else:
                continue
        all_data.extend(data)
        if page * 12 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db(data):
    tids = [tarde[13] for tarde in data]
    used_tids = set(SYFTrade.objects.filter(trans_id__in=tids).values_list("trans_id", flat=True))
    # 插入db
    alist = []
    for t in data:
        if t[13] not in used_tids:
            obj = SYFTrade(
                merchant_name=t[1],
                merchant_receipt=t[2],
                settlement_type=t[3],
                account_type=t[4],
                pay_status=t[5],
                agent_code=t[6],
                agent_name=t[7],
                pos_type=t[8],
                yun=t[9],
                site_id=t[10],
                terminal=t[11],
                trade_date=t[12],
                trans_id=t[13],
                trade_type=t[14],
                consume_type=t[15],
                card_code=t[16],
                card_type=t[17],
                trade_rmb=t[18],
                trade_fee=t[19],
                trade_status=t[20],
                trade_card_type=t[21],
                auth_status=t[22],
                card_bank=t[23],
                return_code=t[24],
                return_info=t[25],
                flow_status=t[26],
            )
            alist.append(obj)
    if alist:
        SYFTrade.objects.bulk_create(alist)
