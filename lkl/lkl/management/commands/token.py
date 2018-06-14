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
    "loginPwd": "4002b625908ea27d00f9ee66c3fa841dd07d5adb70bc2a401196a45641c7dfbae89f1b3ed8896d144ef70f1ac1a3b46d2c9b86a813c3bbb701976de69c91fd5e063370296c03beed25ec85de1eb630bdf8141ac802c4b4bc0437c4d1a601ca09300c94c0c0113236f3bb088fc86f7ad5e02ddc119ef96507895624550ffe3588",
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
