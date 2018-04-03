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
from xyf.models import SYFTrade, SYFTerminal
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
    交易管理--激活商户管理
    """

    @wrapper_raven
    def handle(self, *args, **options):
        print "__xyf terminal"
        if not token:
            print "no token!!"
            return
        cookies = get_cookies(token)
        terminal_data = get_terminal_data(cookies)
        write_to_db_terminal(terminal_data)


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


def get_activate_terminal(cookies, page):
    url = "http://sddl.postar.cn/qryActiveUserList.tran"
    data = {
        "OPERATING": "stlw/activeUserList.jsp",
        "pageNum": "%s" % page,
        "numPerPage": "12",
        "CAMID": "",
        "MERCID": "",
        "MERCNAM": "",
        "TOPAGENTID": "",
        "PAY_FLAG": "",
        "TERMPHYNO": "",
        "BINDTIMESTA": "",
        "BINDTIMEEND": "",
        "PAYDATESTA": "",
        "PAYDATEEND": "",
        "STANDARD_FLAG": "",
    }
    r = requests.post(url, data=data, cookies=cookies)
    html = r.content.decode("utf-8")
    soup = BeautifulSoup(html)
    data = []
    total = r1(ur"共\[(\d+)\]条", html)
    print "total", total
    if not total or not total.isdigit():
        disable_token(token)
    content = soup.find("div", class_="pageContent")
    tbody = content.find("tbody")
    if tbody:
        for line in tbody.find_all("tr"):
            tmp = []
            for td in line.find_all("td"):
                tmp.append(td.text.strip())
            data.append(tmp)
    return data, total


def get_terminal_data(cookies):
    print "get_terminal_data..."
    all_data = []
    page = 1
    while True:
        data, total = get_activate_terminal(cookies, page)
        all_data.extend(data)
        if page * 12 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db_terminal(data):
    tids = [terminal[7] for terminal in data]
    used_tids = set(SYFTerminal.objects.filter(terminal__in=tids).values_list("terminal", flat=True))
    # 插入db
    alist = []
    for t in data:
        if t[7] not in used_tids:
            obj = SYFTerminal(
                promotion=t[0],
                merchant_receipt=t[2],
                merchant_name=t[3],
                agent_code=t[4],
                agent_name=t[5],
                sn_code=t[6],
                terminal=t[7],
                bind_date=t[8],
                recharge_date=t[9],
                recharge_status=t[10],
                trade_rmb=t[11],
                ok_status=t[12]
            )
            alist.append(obj)
        else:
            itmes = SYFTerminal.objects.filter(terminal=t[7])
            if itmes:
                item = itmes[0]
                item.promotion = t[0]
                item.merchant_receipt = t[2]
                item.merchant_name = t[3]
                item.agent_code = t[4]
                item.agent_name = t[5]
                item.sn_code = t[6]
                item.terminal = t[7]
                item.bind_date = t[8]
                item.recharge_date = t[9]
                item.recharge_status = t[10]
                item.trade_rmb = t[11]
                item.ok_status = t[12]
                item.save()
    if alist:
        SYFTerminal.objects.bulk_create(alist)
