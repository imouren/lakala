# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect


def home(request):
    """
    网站首页
    """
    return redirect("user_home")
