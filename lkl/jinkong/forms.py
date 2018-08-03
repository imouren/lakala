# -*- coding: utf-8 -*-
from django import forms
from . import models
from . import dbutils
from easy_select2 import apply_select2


class JKPosAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.JKPos
        fields = ["user", "sn_code", "terminal", "is_activate"]
        widgets = {
            'user': apply_select2(forms.Select)
        }


class JKFenRunAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.JKFenRun
        fields = ["user", "point", "message"]
        widgets = {
            'user': apply_select2(forms.Select)
        }


class JKYunFenRunAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.JKFenRun
        fields = ["user", "point", "message"]
        widgets = {
            'user': apply_select2(forms.Select)
        }


class JKUserRMBAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.JKUserRMB
        fields = ["user", "rmb", "is_auto"]
        widgets = {
            'user': apply_select2(forms.Select)
        }


class BindPosForm(forms.Form):
    code = forms.CharField(max_length=6)
    phone = forms.CharField(max_length=11)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request")
        self.user = request.user
        super(BindPosForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"]

        if len(code) != 6:
            msg = u"序列号输入不正确"
            raise forms.ValidationError(msg)

        self.terminal = dbutils.get_terminal_by_sn_code(code)
        if not self.terminal:
            msg = u"序列号不存在"
            raise forms.ValidationError(msg)
        if not self.terminal.terminal:
            msg = u"请先激活再绑定"
            raise forms.ValidationError(msg)
        code = self.terminal.sn_code
        if dbutils.exists_pos_sn_code(code):
            msg = u"序列号已经被绑定过了"
            raise forms.ValidationError(msg)
        return code

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if len(phone) != 11:
            msg = u"手机号输入不正确"
            raise forms.ValidationError(msg)

        flag = dbutils.exists_merchant_phone(phone)
        if not flag:
            msg = u"商户不存在"
            raise forms.ValidationError(msg)
        return phone

    def clean(self):
        cleaned_data = super(BindPosForm, self).clean()
        phone = self.cleaned_data["phone"]
        merchant_obj = dbutils.get_merchant(self.terminal.merchant_code)
        if merchant_obj:
            if phone != merchant_obj.phone:
                msg = u"商户与手机不一致"
                raise forms.ValidationError(msg)
        else:
            msg = u"无商户"
            raise forms.ValidationError(msg)
        return cleaned_data
