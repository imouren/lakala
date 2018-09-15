# -*- coding: utf-8 -*-
import json
import logging
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from . import dbutils, utils, models
from prov_code import PROV_CODE

logger = logging.getLogger('statistics')


def hhjk_home(request):
    """
    查询输入
    """
    data = {}
    return render(request, "hhjk/search.html", data)


def hhjk_area(request):
    """
    查询结果以及修改入口
    """
    phone = request.GET.get("phone", "")
    merchant_objs = dbutils.get_merchants_by_phone(phone)
    merchants = [obj.merchant_code for obj in merchant_objs]
    merchant_prov_dict = utils.get_current_prov(merchants)
    merchant_list = []
    for obj in merchant_objs:
        info = {
            "merchant_code": obj.merchant_code,
            "merchant_name": obj.merchant_name,
            "prov": merchant_prov_dict.get(obj.merchant_code, "")
        }
        merchant_list.append(info)
    data = {"merchants": merchant_list, "phone": phone}
    return render(request, "hhjk/merchant_prov.html", data)


def hhjk_area_change(request):
    """
    结果页面，修改处理
    """
    merchant = request.GET.get("merchant")
    name = request.GET.get("name")
    phone = request.GET.get("phone")
    data = {"merchant": merchant, "name": name, "phone": phone, "prov_tuple": sorted(PROV_CODE.items())}
    if request.method == 'POST':
        merchant = request.POST.get("merchant")
        prov = request.POST.get("prov", "")
        phone = request.POST.get("phone", "")
        merchant_objs = dbutils.get_merchants_by_phone(phone)
        merchants = [obj.merchant_code for obj in merchant_objs]
        if merchant not in merchants:
            return redirect("hhjk_home")
        prov = prov.isdigit() and int(prov) or 0
        if prov in PROV_CODE:
            utils.change_prov(merchant, prov)
        # return redirect("hhjk_area", phone=phone)
        return redirect(reverse('hhjk_area') + "?phone=%s" % phone)
    else:
        return render(request, "hhjk/change_merchant_prov.html", data)
