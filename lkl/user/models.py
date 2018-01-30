# -*- coding: utf-8 -*-
import uuid
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible



@python_2_unicode_compatible
class UserProfile(models.Model):
    SEX_CHOICE = [
        ('F', u'女'),
        ('M', u'男'),
        ('O', u'其他')
    ]
    user = models.OneToOneField(User)
    phone = models.CharField(u"手机", max_length=20, unique=True)
    name = models.CharField(u"姓名", max_length=20)
    sex = models.CharField(u"性别", choices=SEX_CHOICE, max_length=1)
    is_vip = models.BooleanField(u"是否VIP", default=False)
    code = models.CharField(u"邀请码", max_length=36, unique=True)
    father = models.ForeignKey(User, verbose_name=u"上家", related_name="children", null=True, blank=True)
    update_time = models.DateTimeField(u"创建时间", auto_now=True)
    create_time = models.DateTimeField(u"更新时间", auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            from .utils import generate_code
            # uid = str(uuid.uuid4())
            # self.code = hashlib.md5(uid).hexdigest()
            self.code = generate_code()
        return super(UserProfile, self).save(*args, **kwargs)

    class Meta:
        db_table = "user_profile"
        verbose_name = verbose_name_plural = u"用户属性"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class UserAddress(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户")
    name = models.CharField(u"收件人", max_length=20)
    phone = models.CharField(u"手机", max_length=20)
    telephone = models.CharField(u"座机", max_length=20, blank=True)
    area1 = models.CharField(u"省", max_length=50)
    area2 = models.CharField(u"市", max_length=50)
    area3 = models.CharField(u"县", max_length=50)
    address = models.CharField(u"具体地址", max_length=250)
    post_code = models.CharField(u"邮编", max_length=20, blank=True)
    is_default = models.BooleanField(u"是否默认地址", default=False)
    is_disabled = models.BooleanField(u"是否禁用", default=False)
    update_time = models.DateTimeField(u"创建时间", auto_now=True)
    create_time = models.DateTimeField(u"更新时间", auto_now_add=True)

    class Meta:
        db_table = "user_address"
        verbose_name = verbose_name_plural = u"用户地址"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class UserPos(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户")
    code = models.CharField(u"终端号", max_length=50)
    first_bound = models.BooleanField(u"是否第一次绑定", default=False)
    is_activate = models.BooleanField(u"是否激活", default=False)

    class Meta:
        db_table = "user_pos"
        verbose_name = verbose_name_plural = u"用户POS机"

    def __str__(self):
        return self.code


@python_2_unicode_compatible
class UserTrade(models.Model):
    YA, TUI, FEN = "ya", "tui", "fen"
    TRADE_TYPE_CHOICE = [
        (YA, u"交押金"),
        (TUI, u"退押金"),
        (FEN, u"分红"),
    ]
    user = models.ForeignKey(User, verbose_name=u"用户")
    trade_type = models.CharField(u"交易类型", choices=TRADE_TYPE_CHOICE, max_length=50)
    rmb = models.IntegerField(u"金额")
    message = models.TextField(u"说明")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    class Meta:
        db_table = "user_trade"
        verbose_name = verbose_name_plural = u"用户交易记录"

    def __str__(self):
        return "%s:%s" % (self.trade_type, self.rmb)


@python_2_unicode_compatible
class LKLTrade01(models.Model):
    merchantCode = models.CharField(u"商户编码", max_length=64)
    maintainOrg = models.CharField(u"代理商", max_length=64)
    transId = models.CharField(u"流水号", max_length=64, unique=True)
    cardType = models.CharField(u"渠道", max_length=64)
    transCode = models.CharField(u"交易号", max_length=64)
    termNo = models.CharField(u"终端号", max_length=64)
    payAmt = models.CharField(u"付款金额（分）", max_length=64)
    cardNo = models.CharField(u"交易卡号", max_length=64)
    feeAmt = models.CharField(u"手续费", max_length=64)
    sid = models.CharField(u"SID", max_length=64)
    merchantName = models.CharField(u"商户名称", max_length=64)
    transType = models.CharField(u"业务类型", max_length=64)
    signimage = models.CharField(u"签购单", max_length=1024)
    transAmt = models.CharField(u"交易金额（元）", max_length=64)
    trade_date = models.CharField(u"交易时间", max_length=64)

    class Meta:
        db_table = "lkl_trade01"
        verbose_name = verbose_name_plural = u"收款交易"

    def __str__(self):
        return self.transId
