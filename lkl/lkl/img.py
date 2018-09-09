# -*- coding: utf-8 -*-
import sys
import math
import warnings
from PIL import Image
from io import BytesIO
import requests
from pytesseract import image_to_string


reload(sys)
sys.setdefaultencoding('utf-8')
warnings.filterwarnings("ignore")
WHITE = (255, 255, 255)


def remove_background_rgb2x(aimg, dis=60):
    """
    颜色相近算背景色，去掉
    """
    img = aimg.copy()
    pixdata = img.load()
    w, h = img.size
    res = {}
    for y in range(h):
        for x in range(w):
            p = pixdata[x, y]
            if p in res:
                res[p] += 1
            else:
                res[p] = 1
    points = sorted(res.iteritems(), key=lambda x: -x[1])
    # print points[:5]
    bg_r, bg_g, bg_b = points[0][0]
    for y in range(h):
        for x in range(w):
                r, g, b = pixdata[x, y]
                distance = math.sqrt((bg_r - r)**2 + (bg_g - g)**2 + (bg_b - b)**2)
                if distance < dis:
                    pixdata[x, y] = (255, 255, 255)
    return img


def binarizing(aimg, threshold):
    img = aimg.copy()
    pixdata = img.load()
    w, h = img.size
    # 遍历所有像素，大于阈值的为白色
    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < threshold:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255
    return img


def depointx(aimg):
    # 去孤立点 X轴，同时去掉边缘
    img = aimg.copy()
    pixdata = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            count = 0
            try:
                if pixdata[x, y - 1] == WHITE:  # 上
                    count = count + 1
                if pixdata[x, y + 1] == WHITE:  # 下
                    count = count + 1
                if pixdata[x - 1, y] == WHITE:  # 左
                    count = count + 1
                if pixdata[x + 1, y] == WHITE:  # 右
                    count = count + 1
                if pixdata[x - 1, y - 1] == WHITE:  # 左上
                    count = count + 1
                if pixdata[x - 1, y + 1] == WHITE:  # 左下
                    count = count + 1
                if pixdata[x + 1, y - 1] == WHITE:  # 右上
                    count = count + 1
                if pixdata[x + 1, y + 1] == WHITE:  # 右下
                    count = count + 1
                if count > 4:
                    pixdata[x, y] = WHITE
            except Exception:
                pixdata[x, y] = WHITE
    return img


def depointy(aimg):
    # 去孤立点 Y轴
    img = aimg.copy()
    pixdata = img.load()
    w, h = img.size
    for x in range(1, w - 1):
        for y in range(1, h - 1):
            count = 0
            if pixdata[x, y - 1] == WHITE:  # 上
                count = count + 1
            if pixdata[x, y + 1] == WHITE:  # 下
                count = count + 1
            if pixdata[x - 1, y] == WHITE:  # 左
                count = count + 1
            if pixdata[x + 1, y] == WHITE:  # 右
                count = count + 1
            if pixdata[x - 1, y - 1] == WHITE:  # 左上
                count = count + 1
            if pixdata[x - 1, y + 1] == WHITE:  # 左下
                count = count + 1
            if pixdata[x + 1, y - 1] == WHITE:  # 右上
                count = count + 1
            if pixdata[x + 1, y + 1] == WHITE:  # 右下
                count = count + 1
            if count > 4:
                pixdata[x, y] = WHITE
    return img


def erase_pointy(aimg, n=3):
    # 去两个宽度点 Y轴
    # n 正常字符最小宽度
    img = aimg.copy()
    pixdata = img.load()
    w, h = img.size
    for x in range(1, w - 1):
        points = []
        for y in range(1, h - 1):
            # 遇到白色判断长度
            # 长度不够删除像素
            if pixdata[x, y] == WHITE:
                if len(points) < n:
                    for t_x, t_y in points:
                        pixdata[t_x, t_y] = WHITE
                points = []
            else:
                points.append((x, y))
    return img


def erase_pointx(aimg, n=3):
    # 去两个宽度点 X轴
    # n 正常字符最小宽度
    img = aimg.copy()
    pixdata = img.load()
    w, h = img.size
    for y in range(1, h - 1):
        points = []
        for x in range(1, w - 1):
            # 遇到白色判断长度
            # 长度不够删除像素
            if pixdata[x, y] == WHITE:
                if len(points) < n:
                    for t_x, t_y in points:
                        pixdata[t_x, t_y] = WHITE
                points = []
            else:
                points.append((x, y))
    return img


def get_code(img, threshold=250):
    no_bga_img = remove_background_rgb2x(img, 55)
    for i in range(10):
        no_bga_img = depointx(no_bga_img)
        no_bga_img = depointy(no_bga_img)
    for i in range(5):
        no_bga_img = erase_pointx(no_bga_img, 4)
        no_bga_img = erase_pointy(no_bga_img, 4)
    no_bg_img = no_bga_img.convert("L")
    binary_img = binarizing(no_bg_img, threshold)
    res = image_to_string(binary_img, config='-psm 7 chars')
    return res
