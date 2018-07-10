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


def is_superuser(request):
    if request.user.is_active and request.user.is_superuser:
        return True
    else:
        return False


@admin.register(models.JKMerchant)
class JKMerchantAdmin(admin.ModelAdmin):
    list_display = ["id", "merchant_code", "merchant_name", "phone", "agent_name", "merchant_type", "create_time", "update_time"]
    fields = ["merchant_code", "merchant_name", "phone", "agent_name", "merchant_type", "create_time"]
    search_fields = ["merchant_code", "merchant_name", "phone"]


@admin.register(models.JKTerminal)
class JKTerminalAdmin(admin.ModelAdmin):
    list_display = ["id", "merchant_code", "agent_code", "pos_type", "terminal", "communication", "sn_code", "storage_date", "install_date", "is_xjrw", "business", "fee_receive", "fee_back", "status", "update_time"]
    fields = ["factory", "merchant_code", "agent_code", "pos_type", "terminal", "communication", "sn_code", "storage_date", "install_date", "is_xjrw", "business", "fee_receive", "fee_back", "status"]
    search_fields = ["merchant_code", "sn_code", "terminal"]
    list_filter = ["fee_receive", "fee_back", "status"]


@admin.register(models.JKTrade)
class JKTradeAdmin(admin.ModelAdmin):
    list_display = ["id", "merchant_code", "register_name", "agent_name", "phone", "terminal", "trade_date", "trade_time", "trade_rmb", "trade_type", "trade_status", "is_miao", "return_code", "card_type", "card_code", "card_bank", "trade_fee", "qingfen_rmb", "trans_id", "fenrun", "trade_category", "product", "update_time"]
    fields = ["merchant_code", "register_name", "agent_name", "phone", "terminal", "trade_date", "trade_time", "trade_rmb", "trade_type", "trade_status", "is_miao", "return_code", "card_type", "card_code", "card_bank", "trade_fee", "qingfen_rmb", "trans_id", "fenrun", "trade_category", "product"]
    search_fields = ["trans_id", "terminal", "trade_date", "merchant_code"]


@admin.register(models.JKSettlement)
class JKSettlementAdmin(admin.ModelAdmin):
    list_display = ["id", "trans_id", "merchant_code", "register_name", "start_time", "trade_rmb", "trade_fee", "pay_type", "end_time", "pay_status", "fenrun", "update_time"]
    fields = ["trans_id", "merchant_code", "register_name", "start_time", "trade_rmb", "trade_fee", "pay_type", "end_time", "pay_status", "fenrun"]
    search_fields = ["trans_id", ]


@admin.register(models.JKToken)
class JKTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "token", "is_disabled", "create_time", "update_time"]
    fields = ["token", "is_disabled"]


@admin.register(models.JKPos)
class JKPosAdmin(admin.ModelAdmin):
    form = fms.JKPosAdminForm
    list_display = ["id", "userx", "sn_code", "terminal", "is_activate", "create_time", "update_time"]
    fields = ["user", "sn_code", "terminal", "is_activate"]
    search_fields = ["sn_code", "terminal", "user__username"]
    list_filter = ["is_activate"]
    readonly_fields = ["terminal"]

    def userx(self, obj):
        return '<a href="/admin/jinkong/jkpos/?user_id=%s" target="_blank">%s</a>' % (obj.user.id, obj.user.username)
    userx.allow_tags = True
    userx.short_description = u'用户'


@admin.register(models.JKFenRun)
class JKFenRunAdmin(admin.ModelAdmin):
    form = fms.JKFenRunAdminForm
    list_display = ["user", "point", "message", "create_time", "update_time"]
    fields = ["user", "point", "message"]
    search_fields = ["user__username"]
    list_filter = ["point"]


@admin.register(models.JKYunFenRun)
class JKYunFenRunAdmin(admin.ModelAdmin):
    form = fms.JKYunFenRunAdminForm
    list_display = ["user", "point", "message", "create_time", "update_time"]
    fields = ["user", "point", "message"]
    search_fields = ["user__username"]
    list_filter = ["point"]


@admin.register(models.JKUserRMB)
class JKUserRMBAdmin(admin.ModelAdmin):
    form = fms.JKUserRMBAdminForm
    list_display = ["user", "nickname", "rmb", "is_auto", "create_time", "update_time"]
    fields = ["user", "rmb", "is_auto"]
    search_fields = ["user__username"]
    actions = ['auto_ok_action', 'auto_no_action']

    def auto_ok_action(self, request, queryset):
        for obj in queryset:
            obj.is_auto = True
            obj.save()
    auto_ok_action.short_description = u"自动到账"

    def auto_no_action(self, request, queryset):
        for obj in queryset:
            obj.is_auto = False
            obj.save()
    auto_no_action.short_description = u"不自动到账"

    def nickname(self, obj):
        user = obj.user
        if hasattr(user, "userprofile"):
            name = user.userprofile.name
        else:
            name = u"无"
        return name
    nickname.allow_tags = True
    nickname.short_description = u'昵称'


@admin.register(models.JKProfit)
class JKProfitAdmin(admin.ModelAdmin):
    list_display = ["user", "fenrun_point", "rmb", "merchant_code", "terminal", "trade_date", "trade_rmb", "trade_status", "return_code", "card_type", "trade_fee", "qingfen_rmb", "trans_id", "fenrun", "trade_category", "product", "status", "create_time", "pay_time"]
    fields = ["user", "merchant_code", "terminal", "trade_date", "trade_rmb", "trade_status", "return_code", "card_type", "trade_fee", "qingfen_rmb", "trans_id", "fenrun", "trade_category", "product", "status", "pay_time"]
    search_fields = ["user__username", "terminal", "trans_id", "merchant_code"]
    list_filter = ["status"]


@admin.register(models.JKTiXianOrder)
class JKTiXianOrderAdmin(admin.ModelAdmin):
    list_display = ["user", "user_account", "rmb", "fee", "status", "order_id", "order_type", "create_time", "pay_time", "finish_time"]
    fields = ["user", "user_account", "rmb", "fee", "status", "order_id", "order_type", "pay_time", "finish_time"]
    search_fields = ["user__username", ]
    list_filter = ["status"]
