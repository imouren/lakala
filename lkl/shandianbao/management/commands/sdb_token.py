# -*- coding: utf-8 -*-
import sys
import requests
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
import warnings
from django.core.management.base import BaseCommand
from shandianbao.img import get_code_value
from user.utils import wrapper_raven
from shandianbao import dbutils
from shandianbao import config

reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")

URL = "https://shandianbao.chinapnr.com/supm/login"
LOGIN_URL = "https://shandianbao.chinapnr.com/supm/doLogin"
DATA = {
    "userName": config.SDB_USER,
    "password": config.SDB_PASSWD,
    "captcha": "",
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
IMG_URL = "https://shandianbao.chinapnr.com/supm/util/captcha/image"
MAIN_URL = "https://shandianbao.chinapnr.com/supm/main"

COOKIE = {}

session = requests.Session()


def get_login_page():
    session.get(URL, headers=HEADERS, verify=False)


def get_img():
    url = IMG_URL
    response = session.get(url, headers=HEADERS, verify=False)
    image = Image.open(BytesIO(response.content))
    return image


def get_img_code():
    img = get_img()
    value = get_code_value(img)
    if len(value) == 4:
        return value
    else:
        return get_img_code()


def get_token(code):
    data = DATA.copy()
    data["captcha"] = code.lower()
    res = session.post(LOGIN_URL, data=data, headers=HEADERS, verify=False)
    ok = False
    main_page = session.get(MAIN_URL, headers=HEADERS, verify=False)
    cookies = main_page.cookies
    print "main_page", main_page.cookies
    cookies = session.cookies
    print "session", session.cookies
    try:
        json_data = res.json()
        if json_data["respCode"] == "LOGIN_SUCCESS":
            ok = True
    except Exception:
        pass
    cookies = dict(cookies)
    cookies.update(COOKIE)
    if ok:
        cookies_str = ";".join(["=".join(item) for item in cookies.items()])
        return cookies_str
    else:
        return None


def get_token_good():
    get_login_page()
    code = get_img_code()
    print "code", code
    token = get_token(code)
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
        current_token = dbutils.get_token_code()
        if current_token:
            print "has a token!"
        else:
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
        print "ok"
