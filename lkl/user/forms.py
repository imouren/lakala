# -*- coding: utf-8 -*-
import re
from django import forms
from django.contrib.auth import forms as django_forms
from django.http.request import HttpRequest
from django.urls import reverse
from captcha.fields import CaptchaField
from django.contrib import auth
from . import utils


class LoginForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(max_length=254)
    captcha = CaptchaField()

    def clean(self):
        super(LoginForm, self).clean()
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = auth.authenticate(username=username, password=password)
            if self.user_cache is None:
                msg = u"用户名或者密码错误"
                raise forms.ValidationError(msg)
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=254)
    name = forms.CharField(max_length=254)
    sex = forms.CharField(max_length=254)
    password = forms.CharField(max_length=254)
    password2 = forms.CharField(max_length=254)
    invite_code = forms.CharField(max_length=254)
    captcha = CaptchaField()

    def clean_username(self):
        username = self.cleaned_data["username"]
        username = username.strip()
        pattern = re.compile(r"^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\d{8}$")
        if not pattern.match(username):
            msg = u"手机格式不对"
            raise forms.ValidationError(msg)
        return username

    def clean_name(self):
        name = self.cleaned_data["name"]
        name = name.strip()
        pattern = re.compile(u'[\u4e00-\u9fa5]+')
        if not pattern.match(name) or len(name) < 2:
            msg = u"姓名必须为汉字"
            raise forms.ValidationError(msg)
        return name

    def clean_invite_code(self):
        invite_code = self.cleaned_data["invite_code"]
        invite_code = invite_code.strip()
        lens = len(invite_code)
        if lens not in (6, 32, 11):
            msg = u"邀请码格式不对"
            raise forms.ValidationError(msg)
        is_phone = lens == 11
        self.father_user = utils.get_user_by_code(invite_code, is_phone)
        if not self.father_user:
            msg = u"邀请码不存在"
            raise forms.ValidationError(msg)
        return invite_code

    def clean(self):
        super(RegisterForm, self).clean()
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password and password != password2:
            msg = u"两次密码不一致"
            raise forms.ValidationError(msg)

        username = self.cleaned_data.get("username")
        if not username:
            msg = u"手机格式不对"
            raise forms.ValidationError(msg)
        else:
            username = username.strip()
            user = utils.get_user_by_username(username)
            if user is not None:
                msg = u"该用户已被注册"
                raise forms.ValidationError(msg)
        return self.cleaned_data

    def get_father_user(self):
        return self.father_user


class UserPosForm(forms.Form):
    code = forms.CharField(max_length=50)
    captcha = CaptchaField()

    def clean_code(self):
        super(UserPosForm, self).clean()
        code = self.cleaned_data.get('code')

        if len(code) != 16:
            msg = u"终端号不正确"
            raise forms.ValidationError(msg)

        if utils.exists_pos_code(code):
            msg = u"该终端号已经被绑定过了"
            raise forms.ValidationError(msg)
        return self.cleaned_data
