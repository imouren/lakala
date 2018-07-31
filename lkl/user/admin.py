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


class MyUserAdmin(UserAdmin):

    def user_change_password(self, request, id, from_url=""):
        user = self.get_object(request, unquote(id))
        operator = request.user
        if user.is_superuser and user.id != operator.id:
            raise PermissionDenied
        return UserAdmin.user_change_password(self, request, id)


admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "namex", "fatherx", "phone", "sex", "fenrun", "max_num", "current_num", "create_time"]
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
            return '<a href="/admin/user/userprofile/?father__id__exact=%s" target="_blank">%s</a>' % (obj.father.id, obj.father.userprofile.name)
        else:
            return u"五彩神石"
    fatherx.allow_tags = True
    fatherx.short_description = u'导师'

    def namex(self, obj):
        return '<a href="/admin/user/userprofile/?father__id__exact=%s" target="_blank">%s</a>' % (obj.user.id, obj.name)
    namex.allow_tags = True
    namex.short_description = u'姓名'
    namex.admin_order_field = "name"

    def fenrun(self, obj):
        if hasattr(obj.user, "userfenrun"):
            return "%s__%s" % (obj.user.userfenrun.point, obj.user.userfenrun.rmb)
        else:
            return u"未设置"
    fenrun.allow_tags = True
    fenrun.short_description = u'分润'

    def current_num(self, obj):
        poese = utils.get_user_poses(obj.user)
        num = len(poese)
        if num > 0:
            return '<a href="/admin/user/userpos/?user__id=%s" target="_blank">%s</a>' % (obj.user.id, num)
        else:
            return num
    current_num.allow_tags = True
    current_num.short_description = u'绑定数量'


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
    form = fms.UserPosAdminForm
    list_display = ["user", "userx", "code", "status", "pos_d1", "create_time"]
    fields = ["user", "code"]
    search_fields = ["user__username", "code"]

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            name = obj.user.userprofile.name
        else:
            name = obj.user
        return u'<a href="/admin/user/userpos/?user_id=%s" target="_blank">%s</a>' % (obj.user.id, name)
    userx.allow_tags = True
    userx.short_description = u'用户姓名'

    def pos_d1(self, obj):
        return u'<a href="/admin/user/lkld1/?q=%s" target="_blank">查看</a>' % obj.code
    pos_d1.allow_tags = True
    pos_d1.short_description = u'D1交易'

    def status(self, obj):
        s = dbutils.get_terminal_status(obj.code)
        return s
    status.allow_tags = True
    status.short_description = u'状态'


admin.site.register(models.UserPos, UserPosAdmin)


class UserFenRunAdmin(admin.ModelAdmin):
    form = fms.UserFenRunFrom
    list_display = ["user", "userx", "fatherx", "point", "rmb", "message", "create_time", "update_time"]
    fields = ["user", "point", "rmb", "message"]
    list_filter = ["point", "rmb"]
    search_fields = ["user__username"]

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户姓名'

    def fatherx(self, obj):
        if hasattr(obj.user, "userprofile"):
            p = obj.user.userprofile
            if p.father and hasattr(obj.user, "userprofile"):
                return '<a href="/admin/user/userfenrun/?user__id__exact=%s" target="_blank">%s</a>' % (p.father.id, p.father.userprofile.name)
            else:
                return u"五彩神石"
        else:
            return u"五彩神石"
    fatherx.allow_tags = True
    fatherx.short_description = u'导师'


class UserAlipayAdmin(admin.ModelAdmin):
    list_display = ["user", "userx", "account", "name", "create_time", "update_time"]
    fields = ["user", "account", "name"]
    search_fields = ["user__username"]

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户姓名'


admin.site.register(models.UserFenRun, UserFenRunAdmin)
admin.site.register(models.UserAlipay, UserAlipayAdmin)


class LKLTerminalAdmin(admin.ModelAdmin):
    list_display = ["merchant_code", "merchant_name", "maintain", "terminal", "category", "terminal_type", "open_date", "close_date", "is_give", "is_ok", "ok_date"]
    fields = list_display
    list_filter = ["is_give", "is_ok"]
    search_fields = ["terminal", "merchant_code"]


class LKLD0Admin(admin.ModelAdmin):
    list_display = ["merchant_code", "merchant_name", "maintain", "maintain_code", "trans_id", "category", "draw_date", "draw_rmb", "fee_rmb", "real_rmb", "trans_type", "trans_status"]
    fields = list_display
    search_fields = ["merchant_code", "draw_date"]


class LKLD1Admin(admin.ModelAdmin):
    list_display = ["agent", "merchant_code", "merchant_name", "maintain", "maintain_code", "trans_id", "terminal_num", "draw_date", "draw_rmb", "fee_rmb", "fee_rate", "fee_max", "card_type", "pay_date", "pos_type", "terminal"]
    fields = list_display
    search_fields = ["terminal", "merchant_code", "pay_date"]


admin.site.register(models.LKLTerminal, LKLTerminalAdmin)
admin.site.register(models.LKLD0, LKLD0Admin)
admin.site.register(models.LKLD1, LKLD1Admin)


class UserRMBAdmin(admin.ModelAdmin):
    list_display = ["user", "userx", "rmb", "child_rmb", "create_time", "update_time"]
    fields = ["user", "rmb", "child_rmb"]
    search_fields = ["user__username"]

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户姓名'


class ProfitD1Admin(admin.ModelAdmin):
    list_display = ["user", "trans_id", "fenrun_point", "fenrun_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "card_type", "pay_date", "terminal", "status", "create_time", "pay_time"]
    fields = ["user", "trans_id", "fenrun_point", "fenrun_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "card_type", "pay_date", "terminal", "status", "pay_time"]
    search_fields = ["user__username", "terminal", "merchant_code", "trans_id"]
    list_filter = ["status"]


class ProfitD0Admin(admin.ModelAdmin):
    list_display = ["user", "trans_id", "fenrun_point", "fenrun_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "real_rmb", "trans_type", "trans_status", "status", "create_time", "pay_time"]
    fields = ["user", "trans_id", "fenrun_point", "fenrun_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "real_rmb", "trans_type", "trans_status", "status", "pay_time"]
    search_fields = ["user__username", "merchant_code", "trans_id"]
    list_filter = ["status"]


class ChildProfitD1Admin(admin.ModelAdmin):
    list_display = ["user", "father", "trans_id", "fenrun_point", "fenrun_rmb", "fenrun_father_point", "fenrun_father_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "card_type", "pay_date", "terminal", "status", "create_time", "pay_time"]
    fields = ["user", "trans_id", "fenrun_point", "fenrun_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "card_type", "pay_date", "terminal", "status", "pay_time"]
    search_fields = ["user__username", "terminal", "merchant_code", "trans_id"]
    list_filter = ["status"]


class ChildProfitD0Admin(admin.ModelAdmin):
    list_display = ["user", "father", "trans_id", "fenrun_point", "fenrun_rmb", "fenrun_father_point", "fenrun_father_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "real_rmb", "trans_type", "trans_status", "status", "create_time", "pay_time"]
    fields = ["user", "trans_id", "fenrun_point", "fenrun_rmb", "rmb", "merchant_code", "draw_date", "draw_rmb", "fee_rmb", "real_rmb", "trans_type", "trans_status", "status", "pay_time"]
    search_fields = ["user__username", "merchant_code", "trans_id"]
    list_filter = ["status"]


class TiXianOrderAdmin(admin.ModelAdmin):
    list_display = ["user", "userx", "user_account", "rmb", "fee", "pay_rmb", "status", "order_type", "create_time", "pay_time", "finish_time"]
    fields = ["user", "rmb", "fee", "user_account", "status", "order_type", "pay_time", "finish_time"]
    search_fields = ["user__username"]
    list_filter = ["status"]
    actions = ['make_finished']

    all_fields = [f.name for f in models.TiXianOrder._meta.get_fields()]
    readonly_fields = all_fields

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户姓名'

    def get_readonly_fields(self, request, obj=None):
        if is_superuser(request):
            return []
        else:
            return super(TiXianOrderAdmin, self).get_readonly_fields(request, obj)

    def get_actions(self, request):
        actions = super(TiXianOrderAdmin, self).get_actions(request)
        is_keep = request.user.is_superuser or request.user.username in ["13311368820"]
        if not is_keep:
            if 'make_finished' in actions:
                del actions['make_finished']
        return actions

    def make_finished(self, request, queryset):
        for obj in queryset:
            if obj.status == "PD":
                obj.status = 'SU'
                obj.finish_time = datetime.now()
                obj.save()
    make_finished.short_description = u"打款完成"


class FenRunOrderAdmin(admin.ModelAdmin):
    list_display = ["userx", "childx", "point", "rmb", "status", "create_time", "pass_time", "finish_time"]
    fields = ["user", "child", "point", "rmb", "status", "pass_time", "finish_time"]
    search_fields = ["child__username"]
    list_filter = ["status"]
    actions = ['make_finished']

    all_fields = [f.name for f in models.FenRunOrder._meta.get_fields()]
    readonly_fields = all_fields

    def userx(self, obj):
        if obj.user and hasattr(obj.user, "userprofile"):
            return obj.user.userprofile.name
        else:
            return obj.user
    userx.allow_tags = True
    userx.short_description = u'用户'

    def childx(self, obj):
        if obj.child and hasattr(obj.child, "userprofile"):
            return obj.child.userprofile.name
        else:
            return obj.child
    childx.allow_tags = True
    childx.short_description = u'下家'

    def get_readonly_fields(self, request, obj=None):
        if is_superuser(request):
            return []
        else:
            return super(FenRunOrderAdmin, self).get_readonly_fields(request, obj)

    def get_actions(self, request):
        actions = super(FenRunOrderAdmin, self).get_actions(request)
        is_keep = request.user.is_superuser or request.user.username in ["13311368820"]
        if not is_keep:
            if 'make_finished' in actions:
                del actions['make_finished']
        return actions

    def make_finished(self, request, queryset):
        for obj in queryset:
            if obj.status == "WAIT":
                # 设置分润
                dbutils.set_user_fenrun(obj.child, obj.point, obj.rmb)
                obj.status = "PASS"
                obj.pass_time = datetime.now()
                obj.save()
                obj.status = 'OK'
                obj.finish_time = datetime.now()
                obj.save()
    make_finished.short_description = u"审核通过"


admin.site.register(models.UserRMB, UserRMBAdmin)
admin.site.register(models.ProfitD1, ProfitD1Admin)
admin.site.register(models.ProfitD0, ProfitD0Admin)
admin.site.register(models.ChildProfitD1, ChildProfitD1Admin)
admin.site.register(models.ChildProfitD0, ChildProfitD0Admin)
admin.site.register(models.TiXianOrder, TiXianOrderAdmin)
admin.site.register(models.FenRunOrder, FenRunOrderAdmin)


class SLKLTokenAdmin(admin.ModelAdmin):
    list_display = ["token", "is_disabled", "create_time", "update_time"]
    fields = ["token", "is_disabled"]
    search_fields = []
    list_filter = ["is_disabled"]


admin.site.register(models.SLKLToken, SLKLTokenAdmin)


@admin.register(models.WXUser)
class WXUserAdmin(admin.ModelAdmin):
    list_display = ["user", "openid", "nickname", "sex", "province", "city", "country", "headimgurl", "update_time"]
    fields = []
    search_fields = ["user__username"]
