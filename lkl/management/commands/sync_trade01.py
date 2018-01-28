# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from optparse import make_option
from lkl import utils
from PIL import Image
from io import BytesIO
import requests
from pytesseract import image_to_string

from django.core.management.base import BaseCommand

URL = "https://mposa.lakala.com/queryTrade"


class Command(BaseCommand):
    """
    同步视频对应主题到redis
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--start',
            action='store',
            dest='start',
            help=''),
        make_option(
            '--end',
            action='store',
            dest='end',
            help=''),
    )


    def handle(self, start, end, *args, **options):
        try:
            start_date = utils.string_to_datetime(start)
            end_date = utils.string_to_datetime(end)
            if end_date < start_date:
                end_date = start_date
        except Exception:
            start_date = end_date = datetime.now()
        diff = end_date - start_date
        # 登陆操作
        for i in (diff.days + 1):
            adate = start_date + timedelta(i)
            adate_str = utils.datetime_to_string(adate)
            # 同步数据操作
        print "ok"


def init_table(threshold=200):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    return table


def get_code_value(img_url):
    response = requests.get(img_url)
    im = Image.open(BytesIO(response.content))
    im = im.convert('L')
    binary_image = im.point(init_table(), '1')
    binary_image.show()
    value = image_to_string(binary_image, config='-psm 7 chars')
    print value