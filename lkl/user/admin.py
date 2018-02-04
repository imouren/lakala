# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
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


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "fatherx", "phone", "sex", "is_vip", "code", "max_num", "create_time"]
    fields = ["user", "phone", "name", "sex", "is_vip", "father", "max_num"]
    search_fields = ["name", "phone"]
    all_fields = [f.name for f in models.UserProfile._meta.get_fields()]
    all_fields.remove("max_num")
    readonly_fields = all_fields

    def get_readonly_fields(self, request, obj=None):
        if is_superuser(request):
            return []
        else:
            return super(UserProfileAdmin, self).get_readonly_fields(request, obj)

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
    search_fields = ["user__username", "code"]

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户'


admin.site.register(models.UserPos, UserPosAdmin)


class UserFenRunAdmin(admin.ModelAdmin):
    form = fms.UserFenRunFrom
    list_display = ["user", "point", "rmb", "message", "create_time", "update_time"]
    fields = ["user", "point", "rmb", "message"]
    list_filter = ["point", "rmb"]
    search_fields = ["user__username"]


admin.site.register(models.UserFenRun, UserFenRunAdmin)
