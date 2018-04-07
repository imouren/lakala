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
