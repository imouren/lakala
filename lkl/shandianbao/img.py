# -*- coding: utf-8 -*-
import warnings
import time
from PIL import Image
from io import BytesIO
import requests
from pytesseract import image_to_string


IMG_URL = "https://shandianbao.chinapnr.com/supm/util/captcha/image"
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

warnings.filterwarnings("ignore")


def init_table(threshold=250):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table


def get_code_value(img, threshold=200):
    im = img.convert('L')
    binary_image = im.point(init_table(threshold), '1')
    value = image_to_string(binary_image, config='-psm 7 chars')
    if len(value) == 4:
        return value
