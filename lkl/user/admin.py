# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.template.loader import render_to_string
from easy_select2 import select2_modelform
from suit.admin import SortableTabularInline
from . import models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "fatherx", "phone", "sex", "is_vip", "code", "create_time"]
    fields = ["user", "phone", "name", "sex", "is_vip", "father"]
    search_fields = ["name", "phone"]

    def fatherx(self, obj):
        if obj.father and hasattr(obj.user, "userprofile"):
            return obj.father.userprofile.name
        else:
            return u"五彩神石"
    fatherx.allow_tags = True
    fatherx.short_description = u'导师'


admin.site.register(models.UserProfile, UserProfileAdmin)


class LKLTrade01ileAdmin(admin.ModelAdmin):
    list_display = [
        "merchantCode", "maintainOrg", "transId",
        "cardType", "transCode", "termNo", "payAmt",
        "cardNo", "feeAmt", "sid", "merchantName",
        "transType", "transAmt", "trade_date"]
    fields = list_display
    list_filter = ["cardType", "transType"]
    search_fields = ["termNo", "merchantCode", "transId", "trade_date"]


admin.site.register(models.LKLTrade01, LKLTrade01ileAdmin)


class UserPosAdmin(admin.ModelAdmin):
    list_display = ["userx", "code"]
    fields = list_display

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户'

admin.site.register(models.UserPos, UserPosAdmin)
