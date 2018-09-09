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
from shandianbao.models import SDBTerminal
from user.utils import wrapper_raven
from shandianbao.dbutils import get_token_code, disable_token


reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

TIMEOUT = 120  # 超时时间
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, sdch, br",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    'Content-type': 'application/x-www-form-urlencoded',
    'Host': 'shandianbao.chinapnr.com',
    'Origin': 'https://shandianbao.chinapnr.com',
    'Referer': 'https://shandianbao.chinapnr.com/supm/main/index',
    'X-Requested-With': 'XMLHttpRequest',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) C,hrome/43.0.2357.124 Safari/537.36",
}
DAYS = 1
token = get_token_code()


class Command(BaseCommand):
    """
    数据来源https://shandianbao.chinapnr.com/supm/TRD101/index
    终端管理 --- 终端明细查询 只选2018年
    POST https://shandianbao.chinapnr.com/supm/TER101/control
    terId=&bindFlag=&isActive=&yearBatchno=2018&pageIndex=2
    """

    @wrapper_raven
    def handle(self, *args, **options):
        print "__sdb terminal"
        if not token:
            print "no token!!"
            return

        cookies = get_cookies(token)
        terminal_data = get_terminal_data(cookies)
        write_to_db_terminal(terminal_data)
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


def get_activate_trade(cookies, page):
    url = "https://shandianbao.chinapnr.com/supm/TER101/control"
    data = {
        "pageIndex": page,
        "terId": "",
        "bindFlag": "",
        "isActive": "",
        "yearBatchno": "2018",
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


def get_terminal_data(cookies):
    print "get_terminal_data..."
    all_data = []
    page = 1
    retry = 3
    while True:
        try:
            data, total = get_activate_trade(cookies, page)
        except Exception, e:
            print e
            retry -= 1
            if retry < 0:
                break
            else:
                continue
        all_data.extend(data)
        if page * 10 >= total:
            break
        page += 1
        time.sleep(0.2)
    return all_data


def write_to_db_terminal(data):
    pk_index = 1
    tids = [terminal[pk_index] for terminal in data]
    used_tids = set(SDBTerminal.objects.filter(terminal__in=tids).values_list("terminal", flat=True))
    # 插入db
    alist = []
    same_code = set()
    for t in data:
        terminal = t[pk_index]
        if terminal in same_code:
            print "same code", terminal
            continue
        else:
            same_code.add(terminal)
        if terminal not in used_tids:
            obj = SDBTerminal(
                terminal=t[1],
                batch=t[2],
                company=t[3],
                pos_type=t[4],
                pos_version=t[5],
                agent=t[6],
                agent_name=t[7],
                bind_status=t[8],
                activate_status=t[9],
                bind_merchant=t[10],
                bind_time=t[11],
            )
            alist.append(obj)
        else:
            itmes = SDBTerminal.objects.filter(terminal=t[pk_index])
            if itmes:
                item = itmes[0]
                item.terminal = t[1],
                item.batch = t[2],
                item.company = t[3],
                item.pos_type = t[4],
                item.pos_version = t[5],
                item.agent = t[6],
                item.agent_name = t[7],
                item.bind_status = t[8],
                item.activate_status = t[9],
                item.bind_merchant = t[10],
                item.bind_time = t[11],
                item.save()
    if alist:
        SDBTerminal.objects.bulk_create(alist)
