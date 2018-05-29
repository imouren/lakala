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
from xyf import forms as fms


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
    fields = ["promotion", "merchant_receipt", "merchant_name", "sn_code", "terminal", "bind_date", "recharge_date", "recharge_status", "trade_rmb", "ok_status"]
    search_fields = ["sn_code", "terminal", "bind_date"]
    list_filter = []

    def get_queryset(self, request):
        queryset = super(SYFTerminalAdmin, self).get_queryset(request)
        queryset = queryset.extra({'trade_rmb': "CAST(trade_rmb as DECIMAL)"})
        return queryset


class SYFTradeAdmin(admin.ModelAdmin):
    list_display = ["merchant_name", "merchant_receipt", "settlement_type", "account_type", "pay_status", "agent_code", "agent_name", "pos_type", "yun", "site_id", "terminal", "trade_date", "trans_id", "trade_type", "consume_type", "card_code", "card_type", "trade_rmb", "trade_fee", "trade_status", "trade_card_type", "auth_status", "card_bank", "return_code", "return_info", "flow_status"]
    fields = list_display
    search_fields = ["trans_id", "terminal", "trade_date"]
    list_filter = []


admin.site.register(models.SYFTerminal, SYFTerminalAdmin)
admin.site.register(models.SYFTrade, SYFTradeAdmin)


@admin.register(models.XYFPos)
class XYFPosAdmin(admin.ModelAdmin):
    form = fms.XYFPosAdminForm
    list_display = ["user", "sn_code", "terminal", "is_activate", "create_time", "update_time"]
    fields = ["user", "sn_code", "terminal", "is_activate"]
    search_fields = ["sn_code", "terminal", "user__username"]
    list_filter = ["is_activate"]
    readonly_fields = ["terminal"]


@admin.register(models.XYFFenRun)
class XYFFenRunAdmin(admin.ModelAdmin):
    form = fms.XYFFenRunAdminForm
    list_display = ["user", "point", "message", "create_time", "update_time"]
    fields = ["user", "point", "message"]
    search_fields = ["user__username"]
    list_filter = ["point"]


@admin.register(models.XYFUserRMB)
class XYFUserRMBAdmin(admin.ModelAdmin):
    list_display = ["user", "rmb", "is_auto", "create_time", "update_time"]
    fields = ["user", "rmb", "is_auto"]
    search_fields = ["user__username"]


@admin.register(models.XYFProfit)
class XYFProfitAdmin(admin.ModelAdmin):
    list_display = ["user", "fenrun_point", "rmb", "terminal", "trade_date", "trans_id", "trade_rmb", "trade_fee", "trade_status", "trade_card_type", "return_code", "status", "create_time", "pay_time"]
    fields = ["user", "terminal", "trade_date", "trans_id", "trade_rmb", "trade_fee", "trade_status", "trade_card_type", "return_code", "status", "pay_time"]
    search_fields = ["user__username", "terminal", "trans_id"]
    list_filter = ["status"]
