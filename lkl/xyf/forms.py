# -*- coding: utf-8 -*-
from django import forms
from . import models
from easy_select2 import apply_select2


class XYFPosAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.XYFPos
        fields = ["user", "sn_code", "terminal", "is_activate"]
        widgets = {
            'user': apply_select2(forms.Select)
        }


class XYFFenRunAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.XYFFenRun
        fields = ["user", "point", "message"]
        widgets = {
            'user': apply_select2(forms.Select)
        }


class XYFUserRMBAdminForm(forms.ModelForm):
    """
    for admin
    """
    class Meta:
        model = models.XYFUserRMB
        fields = ["user", "rmb", "is_auto"]
        widgets = {
            'user': apply_select2(forms.Select)
        }
