# -*- coding: utf-8 -*-
import sys
import requests
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
import random
import warnings
from django.core.management.base import BaseCommand
from lkl.img import get_code
from user.utils import wrapper_raven
from user import dbutils

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

URL = "https://s.lakala.com/"
LOGIN_URL = "https://s.lakala.com/website_login.action"
DATA = {
    "loginId": "hcddl15",
    "loginPwd": "1d475830bc4a91e0469b1f3d733880323e606d18019ab93c8882a553908277a3dd4ee9876f0ee82680f525d79cbc076a905876b8060485e540f8f6c78102eb4e0420bfdbf2ea5bdc13f9548ede9468c66a50e292eb5189a1ddb7f02258a1a6c8a50da0e30fa7fedaade3cd52ce5cc31e8621763a285952b5958cc877472ae3e2 650ca22e54dfc387375311047bca01a04876d00dc41f3a1eb7c468481995da77e05bd3d098bdd6aa2289eb123cb2e3d47e4362475155db92ededd80f81fe72bf5bfd7dd891b02ab1c92e81fa001c44bb3e9fd31cc5111965b31888d8e6e2064507102652f51a6f99b5f6cc30118b0a0cccd04171bd332cfc363238240a165714 725e7686837caf8c4434f552e0f3599150ee6d5234ad1c12db4a5859932256335227b6ef986542fc86655a4a2e819191803b0a8e682230b4ace4678f07b84221060f74df5667358cfc6e4cb3a221b5a3c7e9b7f97c68143c5d03c8d69136f74413fbfde87f3e5d2b78deb81398147fd9c246ed73f2fea9b985f2de97e0798c51",
    "phoneCode": "",
    "phoneShow": "",
    "isdls": "1"
}
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
IMG_URL = "https://s.lakala.com/rand.action?tempStr="


def get_cookies():
    res = requests.get(URL, headers=HEADERS, verify=False)
    cookies = res.cookies
    return cookies


def get_img(cookies):
    url = IMG_URL + str(random.random())
    response = requests.get(url, cookies=cookies, headers=HEADERS, verify=False)
    image = Image.open(BytesIO(response.content))
    return image


def get_img_code(cookies):
    img = get_img(cookies)
    value = get_code(img)
    if len(value) == 4:
        return value
    else:
        return get_img_code(cookies)


def get_token(code, cookies):
    data = DATA.copy()
    data["random"] = code.lower()
    res = requests.post(LOGIN_URL, data=data, cookies=cookies, headers=HEADERS, verify=False)
    token = res.url
    if "8080" in token:
        return token
    else:
        return None


def get_token_good():
    cookies = get_cookies()
    code = get_img_code(cookies)
    print "code", code
    token = get_token(code, cookies)
    print "token", token
    return token


class Command(BaseCommand):
    """
    token保存
    """
    # @wrapper_raven
    def handle(self, *args, **options):
        print "__token"
        print datetime.now()
        times = 0
        token = get_token_good()
        while token is None:
            token = get_token_good()
            times += 1
            time.sleep(5)
            if times >= 15:
                break
        if token:
            dbutils.add_token(token)
        else:
            print "token is None"
        dbutils.del_token()
        print "ok"
