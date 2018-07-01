# -*- coding: utf-8 -*-
import sys
import warnings
import requests
from bs4 import BeautifulSoup
from lkl import utils, config
from jinkong.dbutils import get_token_code, disable_token
from .prov_code import PROV_CODE


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


def get_cookies(cookie_string):
    cookies = {}
    for cookie in cookie_string.split(";"):
        cookie = cookie.strip()
        k, v = cookie.split("=", 1)
        cookies[k] = v
    return cookies


def _get_merchant_prov(cookies, merchant):
    url = "http://119.18.194.36/miniIf/miniModifyPlace?mno=%s" % merchant
    r = requests.get(url, cookies=cookies)
    html = r.content.decode("utf-8")
    soup = BeautifulSoup(html)
    aform = soup.find(id="mercInfoForm")
    div = aform.find_all("div")[2]
    prov = div.find_all("label")[1].text
    return prov


def get_current_prov(merchants):
    token = get_token_code()
    cookies = get_cookies(token)
    res = {}
    for merchant in merchants:
        prov = _get_merchant_prov(cookies, merchant)
        res[merchant] = prov
    return res


def change_prov(merchant, province):
    token = get_token_code()
    cookies = get_cookies(token)
    data = {
        "province": province,
        "mercId": merchant
    }
    url = "http://119.18.194.36/miniIf/miniSavePlaceData"
    r = requests.post(url, data=data, cookies=cookies)
    return r.ok
