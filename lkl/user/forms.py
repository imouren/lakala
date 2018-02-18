# -*- coding: utf-8 -*-
import re
from django import forms
from django.contrib.auth import forms as django_forms
from django.http.request import HttpRequest
from django.urls import reverse
from easy_select2 import select2_modelform, apply_select2
from captcha.fields import CaptchaField
from django.contrib import auth
from . import utils
from . import models


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

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        self.user = request.user
        super(UserPosForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"]

        if len(code) != 16:
            msg = u"终端号不正确"
            raise forms.ValidationError(msg)

        if utils.exists_pos_code(code):
            msg = u"该终端号已经被绑定过了"
            raise forms.ValidationError(msg)
        return code

    def clean(self):
        cleaned_data = super(UserPosForm, self).clean()

        if hasattr(self.user, "userprofile"):
            max_num = self.user.userprofile.max_num
        else:
            max_num = 0
        current_num = utils.get_user_poses(self.user)
        if len(current_num) >= max_num:
            msg = u"最多可绑%s机器" % max_num
            raise forms.ValidationError(msg)
        return cleaned_data


class UserPosAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.UserPos
        fields = ["user", "code"]
        widgets = {
            'user': apply_select2(forms.Select)
        }

    def clean_code(self):
        code = self.cleaned_data["code"]

        if len(code) != 16:
            msg = u"终端号不正确"
            raise forms.ValidationError(msg)

        if utils.exists_pos_code(code):
            msg = u"该终端号已经被绑定过了"
            raise forms.ValidationError(msg)
        return code

    def clean(self):
        cleaned_data = super(UserPosAdminForm, self).clean()

        if hasattr(self.user, "userprofile"):
            max_num = self.user.userprofile.max_num
        else:
            max_num = 0
        current_num = utils.get_user_poses(self.user)
        if len(current_num) >= max_num:
            msg = u"最多可绑%s机器" % max_num
            raise forms.ValidationError(msg)
        return cleaned_data


class UserFenRunFrom(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.UserFenRun
        fields = ["user", "point", "rmb", "message"]
        widgets = {
            'user': apply_select2(forms.Select),
            'point': apply_select2(forms.Select),
            'rmb': apply_select2(forms.Select),
        }

    def clean_point(self):
        point = self.cleaned_data["point"]
        user = self.cleaned_data["user"]
        try:
            father = user.userprofile.father
        except Exception, e:
            print e
            father = None
        if father is None:
            father_point = "10.0"
        else:
            if hasattr(father, "userfenrun"):
                father_point = father.userfenrun.point
            else:
                father_point = "5"
        if float(point) > float(father_point):
            msg = u"提点不能高于上家"
            raise forms.ValidationError(msg)
        return point

    def clean_rmb(self):
        rmb = self.cleaned_data["rmb"]
        user = self.cleaned_data["user"]
        try:
            father = user.userprofile.father
        except Exception, e:
            print e
            father = None
        if father is None:
            father_rmb = "1.0"
        else:
            if hasattr(father, "userfenrun"):
                father_rmb = father.userfenrun.rmb
            else:
                father_rmb = "0.0"
        if float(rmb) > float(father_rmb):
            msg = u"现金不能高于上家"
            raise forms.ValidationError(msg)
        return rmb
