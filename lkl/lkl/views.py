# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect


def home(request):
    """
    网站首页
    """
    return HttpResponse(u"欢迎你来到我的生活！")


def wx_js(request):
    """
    JS接口安全域名
    """
    return HttpResponse("kn6YuZIRpnYWeVCO")


def hhjk_wx_js(request):
    """
    JS接口安全域名
    """
    return HttpResponse("1hja9C8HvptXtWzB")


def zzzt_wx_js(request):
    """
    JS接口安全域名
    """
    return HttpResponse("NUerhIBr4nth7bhm")


def fzcj_wx_js(request):
    """
    JS接口安全域名
    """
    return HttpResponse("xLVJtEkSzT6g4IRj")


def taobao_root(request):
    """
    JS接口安全域名
    """
    return HttpResponse("53c122835dcff61529111eff7b4e04f1")
