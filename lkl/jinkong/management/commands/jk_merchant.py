# -*- coding: utf-8 -*-
import sys
import re
import warnings
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from lkl import utils, config
from jinkong.models import JKMerchant
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
    MINIPOS商户查询
    """
    # @wrapper_raven
    def handle(self, *args, **options):
        print "__jk merchant"
        if not token:
            print "no token!!"
            return
        cookies = get_cookies(token)
        data = get_merchant_data(cookies)
        write_to_db_merchant(data)
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


def get_activate_merchant(cookies, page):
    url = "http://119.18.194.36/miniIf/MinilistSs"
    data = {
        "pageSize": "20",
        "pageNum": "%s" % page,
        "prov": "",
        "city": "",
        "mno": "",
        "contNmCn": "",
        "crpIdNo": "",
        "accountNumber": "",
        "mecSts": "",
        "empNm": "",
        "openStartTm": "",
        "openEndTm": "",
        "mecProvCd": "",
        "rat1": "",
        "rat3": "",
        "creStartTm": "",
        "creEndTm": "",
        "mecTyp": "04",
        "isBrush": "",
        "mercOprMbl": "",
        "orgNo": "",
        "depositStatus": "",
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
            for td in line.find_all("td")[:-1]:
                tmp.append(td.text.strip())
            data.append(tmp)
    return data, total


def get_merchant_data(cookies):
    print "get_merchant_data..."
    all_data = []
    page = 1
    retry = 3
    while True:
        try:
            data, total = get_activate_merchant(cookies, page)
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


def write_to_db_merchant(data):
    tids = [x[0] for x in data]
    used_tids = set(JKMerchant.objects.filter(merchant_code__in=tids).values_list("merchant_code", flat=True))
    # 插入db
    alist = []
    same_code = set()
    for t in data:
        if t[0] in same_code:
            print "same code", t[0]
            continue
        else:
            same_code.add(t[0])
        if t[0] not in used_tids:
            obj = JKMerchant(
                merchant_code=t[0],
                merchant_name=t[1],
                phone=t[2],
                agent_name=t[3],
                merchant_type=t[4],
                create_time=t[5],
            )
            alist.append(obj)
        else:
            itmes = JKMerchant.objects.filter(merchant_code__in=t[0])
            if itmes:
                item = itmes[0]
                item.merchant_code = t[0]
                item.merchant_name = t[1]
                item.phone = t[2]
                item.agent_name = t[3]
                item.merchant_type = t[4]
                item.create_time = t[5]
                item.save()
    if alist:
        JKMerchant.objects.bulk_create(alist)
