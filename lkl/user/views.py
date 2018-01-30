# -*- coding: utf-8 -*-
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
from .forms import LoginForm, RegisterForm
from .models import UserProfile
from . import utils


def home(request):
    """
    用户首页
    """
    data = {}
    return render(request, "lkl/index.html", data)


def news(request):
    """
    资讯页
    """
    data = {}
    return render(request, "lkl/news.html", data)


def account(request):
    """
    账户页
    """
    data = {}
    if request.user.is_authenticated:
        return render(request, "lkl/account.html", data)
    else:
        return redirect("user_login")


def loginx(request):
    """
    登陆
    """

    if request.user.is_authenticated:
        return redirect("user_account")
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                request.session['user_name'] = username
                return redirect("user_account")
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data = {"img_url": img_url, "hashkey": hashkey}
    return render(request, "lkl/login.html", data)


def login(request):
    data = {}
    if request.user.is_authenticated:
        return redirect("user_account")
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            auth.login(request, form.get_user())
            return redirect("user_account")
        else:
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/login.html", data)


@login_required
def logout(request):
    auth.logout(request)
    return redirect("user_home")


def register(request):
    data = {}
    if request.user.is_authenticated:
        return redirect("user_account")
    if request.method == 'POST':
        print request.POST
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            sex = form.cleaned_data.get('sex')
            name = form.cleaned_data.get('name')
            user = User.objects.create_user(username=username, password=password)
            user.save()
            UserProfile.objects.create(user=user, phone=user.username, sex=sex, name=name, father=form.get_father_user())
            auth.login(request, user)
            return redirect("user_account")
        else:
            print form.errors
            error = form.errors.get("__all__")
            data.update({"error": error, "errors": form.errors})
    hashkey = CaptchaStore.generate_key()
    img_url = captcha_image_url(hashkey)
    data.update({"img_url": img_url, "hashkey": hashkey})
    return render(request, "lkl/register.html", data)


@login_required
def search_terminal(request):
    data = {}
    if request.method == 'POST':
        q = request.POST.get("q")
        trade_data = utils.get_trade_by_terminal2(q)
        data["trade"] = trade_data
    return render(request, "lkl/search_terminal.html", data)


@login_required
def bind_pos(request):
    data = {}
    if request.method == 'POST':
        code = request.POST.get("code")
        trade_data = utils.get_trade_by_terminal2(q)
        data["trade"] = trade_data
    return render(request, "lkl/bind_pos.html", data)
