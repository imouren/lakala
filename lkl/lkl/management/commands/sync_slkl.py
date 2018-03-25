# -*- coding: utf-8 -*-
import sys
import re
import warnings
from datetime import datetime, timedelta
import requests
from pytesseract import image_to_string
from django.core.management.base import BaseCommand
from lkl import utils, config
from bs4 import BeautifulSoup
import time
from user.models import LKLTerminal, LKLD0, LKLD1
from user.utils import wrapper_raven


reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

TIMEOUT = 120  # 超时时间
URL = config.SLKL_TOKEN
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
    综合查询--代理商MPOS个人D0
    代理商查询--日报--MPOS个人交易明细
    代理商查询--公共查询--MPOS代理商终端管理
    备注：达标机器激活当天（含）起30天刷卡2万，额外奖励99
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
        parser.add_argument(
            '--table',
            action='store',
            dest='table',
            help=''
        )

    @wrapper_raven
    def handle(self, start, end, table, *args, **options):
        is_none = False
        if start is None or end is None:
            is_none = True
            end_date = datetime.now()
            if table == "terminal_update":
                end_date = end_date - timedelta(3)
                start_date = end_date - timedelta(30)
            else:
                start_date = end_date - timedelta(3)
            start = utils.datetime_to_string(start_date, format_str="%Y-%m-%d")
            end = utils.datetime_to_string(end_date, format_str="%Y-%m-%d")
        print "__sync slkl", start, end, table
        print datetime.now()
        cookies = get_cookies()
        start1 = "".join(start.split("-"))
        end1 = "".join(end.split("-"))
        # D0
        if table in ("d0", "all"):
            d0_data = get_d0_data(cookies, start1, end1)
            write_to_db_d0(d0_data)
        # D1
        if table in ("d1", "all"):
            start_date = utils.string_to_datetime(start1)
            end_date = utils.string_to_datetime(end1)
            diff = end_date - start_date
            if is_none:
                s = -3
            else:
                s = 0
            for i in range(s, diff.days + 1):
                adate = start_date + timedelta(i)
                adate_str = utils.datetime_to_string(adate)
                d1_data = get_d1_data(cookies, adate_str)
                write_to_db_d1(d1_data)
        # 终端
        if table in ("terminal", "terminal_update", "all"):
            terminal_data = get_terminal_data(cookies, start, end)
            write_to_db_terminal(terminal_data)


def r1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)


def get_cookies():
    res = requests.get(URL, headers=HEADERS, verify=False)
    cookies = res.cookies
    return cookies


def get_terminal_data(cookies, start, end):
    """
    代理商查询--公共查询--MPOS代理商终端管理
    """
    print "get_terminal_data..."
    # url_base = "https://nb.lakala.com:8080/lakala-report-agent/nebula/report_view!result.action?orgId=584798&reportId=RPT_8120&panel_panel1=block&beginOpenDate={}&endOpenDate={}&organTypeName=%E7%89%9B%E4%BF%8A%E5%8A%9B13311368820&checkOrgId=584798&ischildren=1&status=-1&isgive=-1&psam_no=&sdbDate=&edbDate=&random={}"
    url_base = "https://nb.lakala.com:8080/lakala-report-agent/nebula/report_view!result.action?orgId=532730&reportId=RPT_8120&panel_panel1=block&beginOpenDate={}&endOpenDate={}&organTypeName=%E5%AE%8F%E6%98%8C%E5%A4%A7%E4%BB%A3%E7%90%86-K&checkOrgId=532730&ischildren=1&status=-1&isgive=-1&psam_no=&sdbDate=&edbDate=&random={}"
    all_data = []
    page = 1
    while True:
        url = url_base.format(start, end, int(time.time() * 1000))
        if page > 1:
            url = url + "&RPT_2120.pageSize=10&RPT_2120.pageNo=%s" % page
        print "page:%s" % page
        print url
        try:
            r = requests.get(url, headers=HEADERS, cookies=cookies, verify=False, timeout=TIMEOUT)
        except:
            print "timeout..."
            continue
        html = r.content.decode("utf-8")
        soup = BeautifulSoup(html)
        data = []
        title = soup.title.string
        print "title", title
        total = r1(ur"共(\d+)条", html)
        print "total", total
        total = int(total)
        tbody = soup.find("tbody")
        if tbody:
            for line in tbody.find_all("tr"):
                tmp = []
                for td in line.find_all("td"):
                    tmp.append(td.text)
                data.append(tmp)
            all_data.extend(data)
        else:
            print "no tbody"
        if page * 10 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db_terminal(data):
    # 商户号0 维护方1 商户注册名称2 产品分类3 终端号4 机具型号5
    # 终端开通时间6 终端关闭时间7 是否赠送8 是否达标9 达标时间10
    # 原有数据
    tids = [terminal[4] for terminal in data]
    used_tids = set(LKLTerminal.objects.filter(terminal__in=tids).values_list("terminal", flat=True))
    # 插入db
    alist = []
    for t in data:
        if t[4] not in used_tids:
            obj = LKLTerminal(
                merchant_code=t[0],
                merchant_name=t[2],
                maintain=t[1],
                terminal=t[4],
                category=t[3],
                terminal_type=t[5],
                open_date=t[6],
                close_date=t[7],
                is_give=t[8],
                is_ok=t[9],
                ok_date=t[10]
            )
            alist.append(obj)
        else:
            itmes = LKLTerminal.objects.filter(terminal=t[4])
            if itmes:
                item = itmes[0]
                item.merchant_code = t[0]
                item.merchant_name = t[2]
                item.maintain = t[1]
                item.category = t[3]
                item.terminal_type = t[5]
                item.open_date = t[6]
                item.close_date = t[7]
                item.is_give = t[8]
                item.is_ok = t[9]
                item.ok_date = t[10]
                item.save()
    if alist:
        LKLTerminal.objects.bulk_create(alist)


def get_d0_data(cookies, start, end):
    """
    综合查询--代理商MPOS个人D0
    """
    print "get_d0_data..."
    # url_base = "https://nb.lakala.com:8080/lakala-report-agent/nebula/report_view!result.action?orgId=584798&reportId=RPT_40022&panel_panel1=block&startDate={}&endDate={}&merchant_code=&discount_standard=-1&mcc_class=-1&organTypeName=%E7%89%9B%E4%BF%8A%E5%8A%9B13311368820&checkOrgId=584798&random={}"
    url_base = "https://nb.lakala.com:8080/lakala-report-agent/nebula/report_view!result.action?orgId=532730&reportId=RPT_40022&panel_panel1=block&startDate={}&endDate={}&merchant_code=&discount_standard=-1&mcc_class=-1&organTypeName=%E5%AE%8F%E6%98%8C%E5%A4%A7%E4%BB%A3%E7%90%86-K&checkOrgId=532730&random={}"
    all_data = []
    page = 1
    while True:
        url = url_base.format(start, end, int(time.time() * 1000))
        if page > 1:
            url = url + "&RPT_40021.pageSize=10&RPT_40021.pageNo=%s" % page
        print "page:%s" % page
        print url
        try:
            r = requests.get(url, headers=HEADERS, cookies=cookies, verify=False, timeout=TIMEOUT)
        except:
            print "timeout ..."
            continue
        html = r.content.decode("utf-8")
        soup = BeautifulSoup(html)
        data = []
        total = r1(ur"共(\d+)条", html)
        print "total", total
        total = int(total)
        tbody = soup.find("tbody")
        if tbody:
            for line in tbody.find_all("tr"):
                tmp = []
                for td in line.find_all("td"):
                    tmp.append(td.text)
                data.append(tmp)
            all_data.extend(data)
        else:
            print "no tbody"
        if page * 10 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db_d0(data):
    # 流水号0   签约机构1 签约机构号2 分类3 商户号4 商户注册名称5
    # 提款日期6 提款金额7 提款手续费8   实扣金额9 交易类型10 交易状态11
    # 原有数据
    tids = [terminal[0] for terminal in data]
    used_tids = set(LKLD0.objects.filter(trans_id__in=tids).values_list("trans_id", flat=True))
    # 插入db
    alist = []
    for t in data:
        if t[0] not in used_tids:
            obj = LKLD0(
                merchant_code=t[4],
                merchant_name=t[5],
                maintain=t[1],
                maintain_code=t[2],
                trans_id=t[0],
                category=t[3],
                draw_date=t[6],
                draw_rmb=t[7],
                fee_rmb=t[8],
                real_rmb=t[9],
                trans_type=t[10],
                trans_status=t[11]
            )
            alist.append(obj)
    if alist:
        LKLD0.objects.bulk_create(alist)


def get_d1_data(cookies, adate):
    """
    代理商查询--日报--MPOS个人交易明细
    """
    print "get_d1_data...", adate
    # url_base = "https://nb.lakala.com:8080/lakala-report-agent/nebula/report_view!result.action?orgId=584798&reportId=RPT_8103&panel_panel1=block&agentDate={}&checkOrgId=584798&organTypeName=%E7%89%9B%E4%BF%8A%E5%8A%9B13311368820&queryChildren=1&random={}"
    url_base = "https://nb.lakala.com:8080/lakala-report-agent/nebula/report_view!result.action?orgId=532730&reportId=RPT_8103&panel_panel1=block&agentDate={}&checkOrgId=532730&organTypeName=%E5%AE%8F%E6%98%8C%E5%A4%A7%E4%BB%A3%E7%90%86-K&queryChildren=1&random={}"
    all_data = []
    page = 1
    while True:
        url = url_base.format(adate, int(time.time() * 1000))
        if page > 1:
            url = url + "&RPT_8103.pageSize=10&RPT_8103.pageNo=%s" % page
        print "date: %s page:%s" % (adate, page)
        print url
        try:
            r = requests.get(url, headers=HEADERS, cookies=cookies, verify=False, timeout=TIMEOUT)
        except:
            print "timeout ..."
            continue
        html = r.content.decode("utf-8")
        soup = BeautifulSoup(html)
        data = []
        total = r1(ur"共(\d+)条", html)
        print "total", total
        total = int(total)
        tbody = soup.find("tbody")
        if tbody:
            for line in tbody.find_all("tr"):
                tmp = []
                for td in line.find_all("td"):
                    tmp.append(td.text)
                data.append(tmp)
            all_data.extend(data)
        else:
            print "no tbody"
        if page * 10 >= total:
            break
        page += 1
        time.sleep(2)
    return all_data


def write_to_db_d1(data):
    # 当前帐号下级代理商0 流水号1 签约机构2 签约机构号3 商户号4 商户注册名5
    # 终端号6 交易日期7 交易金额8 商户手续费9 借贷记标记10 支付时间11 卡应用类型12   PSAM卡号13
    # 原有数据
    # 3月15日修改数据
    # 当前帐号下级代理商0 流水号1 签约机构2 签约机构号3 商户号4 商户注册名5
    # 终端号6 交易日期7 交易金额8 商户手续费9
    # 新增两个  商户签约费率10  封顶手续费 11
    # 借贷记标记12 支付时间13 卡应用类型14   PSAM卡号15
    tids = [terminal[1] for terminal in data]
    used_tids = set(LKLD1.objects.filter(trans_id__in=tids).values_list("trans_id", flat=True))
    # 插入db
    alist = []
    tids_set = set()  # 他的系统有重复流水的
    for t in data:
        if t[1] not in used_tids and t[1] not in tids_set:
            obj = LKLD1(
                agent=t[0],
                trans_id=t[1],
                maintain=t[2],
                maintain_code=t[3],
                merchant_code=t[4],
                merchant_name=t[5],
                terminal_num=t[6],
                draw_date=t[7],
                draw_rmb=t[8],
                fee_rmb=t[9],
                card_type=t[10],
                fee_rate=t[11],
                fee_max=t[12],
                pay_date=t[13],
                pos_type=t[14],
                terminal=t[15]
            )
            alist.append(obj)
            tids_set.add(t[1])
    if alist:
        LKLD1.objects.bulk_create(alist)
