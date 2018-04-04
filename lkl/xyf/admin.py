# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from easy_select2 import select2_modelform
from suit.admin import SortableTabularInline
from . import models
from . import forms as fms
from . import utils, dbutils


def is_superuser(request):
    if request.user.is_active and request.user.is_superuser:
        return True
    else:
        return False


class XYFTokenAdmin(admin.ModelAdmin):
    list_display = ["token", "is_disabled", "create_time", "update_time"]
    fields = ["token", "is_disabled"]
    search_fields = []
    list_filter = ["is_disabled"]


admin.site.register(models.XYFToken, XYFTokenAdmin)


class SYFTerminalAdmin(admin.ModelAdmin):
    list_display = ["promotion", "merchant_receipt", "merchant_name", "sn_code", "terminal", "bind_date", "recharge_date", "recharge_status", "trade_rmb", "ok_status", "update_time"]
    fields = list_display
    search_fields = ["sn_code", "terminal", "bind_date"]
    list_filter = []


class SYFTradeAdmin(admin.ModelAdmin):
    list_display = ["merchant_name", "merchant_receipt", "settlement_type", "account_type", "pay_status", "agent_code", "agent_name", "pos_type", "yun", "site_id", "terminal", "trade_date", "trans_id", "trade_type", "consume_type", "card_code", "card_type", "trade_rmb", "trade_fee", "trade_status", "trade_card_type", "auth_status", "card_bank", "return_code", "return_info", "flow_status"]
    fields = list_display
    search_fields = ["trans_id", "terminal", "trade_date"]
    list_filter = []


admin.site.register(models.SYFTerminal, SYFTerminalAdmin)
admin.site.register(models.SYFTrade, SYFTradeAdmin)
