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
from jinkong.models import JKTerminal
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
    @wrapper_raven
    def handle(self, *args, **options):
        print "__jk terminal"
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


def get_activate_terminal(cookies, page):

    base_url = "http://119.18.194.36/queryPosInfo/queryPosList?pageSize=20&pageNum={}&modNoTemp=&trmNo=&trmSn=&regFlg=&connTyp=&mfrNo=&modNo=&mercSn=&begTranDate=&endTranDate=&begInstallDate=&endInstallDate=&mercOwn=&businessType=&isOrNotfwf=&isReversefwf="
    url = base_url.format(page)
    r = requests.get(url, cookies=cookies)
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


def get_terminal_data(cookies):
    print "get_terminal_data..."
    all_data = []
    page = 1
    retry = 3
    while True:
        try:
            data, total = get_activate_terminal(cookies, page)
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


def write_to_db_terminal(data):
    tids = [terminal[6] for terminal in data]
    used_tids = set(JKTerminal.objects.filter(sn_code__in=tids).values_list("sn_code", flat=True))
    # 插入db
    alist = []
    same_code = set()
    for t in data:
        if t[6] in same_code:
            print "same code", t[6]
            continue
        else:
            same_code.add(t[6])
        if t[6] not in used_tids:
            obj = JKTerminal(
                factory=t[0],
                merchant_code=t[1],
                agent_code=t[2],
                pos_type=t[3],
                terminal=t[4],
                communication=t[5],
                sn_code=t[6],
                storage_date=t[7],
                install_date=t[8],
                is_xjrw=t[9],
                business=t[10],
                fee_receive=t[11],
                fee_back=t[12],
                status=t[13]
            )
            alist.append(obj)
        else:
            itmes = JKTerminal.objects.filter(sn_code=t[6])
            if itmes:
                item = itmes[0]
                item.factory = t[0]
                item.merchant_code = t[1]
                item.agent_code = t[2]
                item.pos_type = t[3]
                item.terminal = t[4]
                item.communication = t[5]
                item.sn_code = t[6]
                item.storage_date = t[7]
                item.install_date = t[8]
                item.is_xjrw = t[9]
                item.business = t[10]
                item.fee_receive = t[11]
                item.fee_back = t[12]
                item.status = t[13]
                item.save()
    if alist:
        JKTerminal.objects.bulk_create(alist)
