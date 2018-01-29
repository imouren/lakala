# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.template.loader import render_to_string
from easy_select2 import select2_modelform
from suit.admin import SortableTabularInline
from . import models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "father", "phone", "name", "sex", "is_vip", "code", "create_time"]
    fields = ["user", "phone", "name", "sex", "is_vip", "father"]
    search_fields = ["name", "phone"]


admin.site.register(models.UserProfile, UserProfileAdmin)


class LKLTrade01ileAdmin(admin.ModelAdmin):
    list_display = [
        "merchantCode", "maintainOrg", "transId",
        "cardType", "transCode", "termNo", "payAmt",
        "cardNo", "feeAmt", "sid", "merchantName",
        "transType", "transAmt", "trade_date"]
    fields = list_display
    search_fields = ["termNo", "merchantCode", "transId"]


admin.site.register(models.LKLTrade01, LKLTrade01ileAdmin)
