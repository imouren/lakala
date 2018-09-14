# -*- coding: utf-8 -*-
from datetime import datetime
from django.contrib import admin
from django import forms
from easy_select2 import select2_modelform
from . import models
from . import forms as fms


@admin.register(models.HHJKMerchant)
class HHJKMerchantAdmin(admin.ModelAdmin):
    list_display = ["id", "merchant_code", "merchant_name", "phone", "agent_name", "merchant_type", "create_time", "update_time"]
    fields = ["merchant_code", "merchant_name", "phone", "agent_name", "merchant_type", "create_time"]
    search_fields = ["merchant_code", "merchant_name", "phone"]


@admin.register(models.HHJKTerminal)
class HHJKTerminalAdmin(admin.ModelAdmin):
    list_display = ["id", "merchant_code", "agent_code", "pos_type", "terminal", "communication", "sn_code", "storage_date", "install_date", "is_xjrw", "business", "fee_receive", "fee_back", "status", "update_time"]
    fields = ["factory", "merchant_code", "agent_code", "pos_type", "terminal", "communication", "sn_code", "storage_date", "install_date", "is_xjrw", "business", "fee_receive", "fee_back", "status"]
    search_fields = ["merchant_code", "sn_code", "terminal"]
    list_filter = ["fee_receive", "fee_back", "status"]


@admin.register(models.HHJKTrade)
class HHJKTradeAdmin(admin.ModelAdmin):
    list_display = ["id", "merchant_code", "register_name", "agent_name", "phone", "terminal", "trade_date", "trade_time", "trade_rmb", "trade_type", "trade_status", "is_miao", "return_code", "card_type", "card_code", "card_bank", "trade_fee", "qingfen_rmb", "trans_id", "fenrun", "trade_category", "product", "update_time"]
    fields = ["merchant_code", "register_name", "agent_name", "phone", "terminal", "trade_date", "trade_time", "trade_rmb", "trade_type", "trade_status", "is_miao", "return_code", "card_type", "card_code", "card_bank", "trade_fee", "qingfen_rmb", "trans_id", "fenrun", "trade_category", "product"]
    search_fields = ["trans_id", "terminal", "trade_date", "merchant_code"]


@admin.register(models.HHJKToken)
class HHJKTokenAdmin(admin.ModelAdmin):
    list_display = ["id", "token", "is_disabled", "create_time", "update_time"]
    fields = ["token", "is_disabled"]
