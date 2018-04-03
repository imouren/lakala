# -*- coding: utf-8 -*-
import json
import logging
import requests
import cPickle as pickle
from datetime import datetime
from urllib import quote_plus
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from .forms import LoginForm, RegisterForm, UserPosForm, UserAlipayForm, TixianRMBForm
from .models import UserProfile, UserPos, UserAlipay, UserFenRun, FenRunOrder, TiXianOrder
from . import utils, dbutils
from lkl import config
from .utils import rclient

logger = logging.getLogger('statistics')


def home(request):
    """
    用户首页
    """
    data = {}
    return render(request, "lkl/index.html", data)
