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
    max_num = models.IntegerField(u"机器上限", default=1)
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
    update_time = models.DateTimeField(u"更新时间", auto_now=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

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
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        return super(UserPos, self).save(*args, **kwargs)

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
class UserFenRun(models.Model):
    POINT_CHOICE = [
        ("5", u"5"),
        ("5.5", u"5.5"),
        ("6", u"6"),
        ("6.5", u"6.5"),
        ("7", u"7"),
        ("7.5", u"7.5"),
        ("8", u"8"),
        ("8.5", u"8.5"),
        ("9", u"9"),
        ("9.5", u"9.5"),
        ("10.0", u"10.0")
    ]
    RMB_CHOICE = [
        ("0.0", u"0.0"),
        ("0.1", u"0.1"),
        ("0.2", u"0.2"),
        ("0.3", u"0.3"),
        ("0.4", u"0.4"),
        ("0.5", u"0.5"),
        ("0.6", u"0.6"),
        ("0.7", u"0.7"),
        ("0.8", u"0.8"),
        ("0.9", u"0.9"),
        ("1.0", u"1.0"),
    ]
    user = models.OneToOneField(User, verbose_name=u"用户")
    point = models.CharField(u"提点", choices=POINT_CHOICE, max_length=50)
    rmb = models.CharField(u"秒到", choices=RMB_CHOICE, max_length=50)
    message = models.TextField(u"说明", blank=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    class Meta:
        db_table = "user_fenrun"
        verbose_name = verbose_name_plural = u"用户分润"

    def __str__(self):
        return "%s:%s" % (self.point, self.rmb)


@python_2_unicode_compatible
class LKLTrade01(models.Model):
    """
    数据来源mposa.lakala.com
    """
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


@python_2_unicode_compatible
class LKLTerminal(models.Model):
    """
    数据来源s.lakala.com
    """
    merchant_code = models.CharField(u"商户号", max_length=64)
    merchant_name = models.CharField(u"商户注册名称", max_length=64)
    maintain = models.CharField(u"维护方", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64, unique=True)
    category = models.CharField(u"产品分类", max_length=64)
    terminal_type = models.CharField(u"机具型号", max_length=64)
    open_date = models.CharField(u"开通时间", max_length=64)
    close_date = models.CharField(u"关闭时间", max_length=64)
    is_give = models.CharField(u"是否赠送", max_length=64)
    is_ok = models.CharField(u"是否达标", max_length=64)
    ok_date = models.CharField(u"达标时间", max_length=64)

    class Meta:
        db_table = "lkl_terminal"
        verbose_name = verbose_name_plural = u"终端管理"

    def __str__(self):
        return self.terminal


@python_2_unicode_compatible
class LKLD0(models.Model):
    """
    数据来源s.lakala.com
    """
    merchant_code = models.CharField(u"商户号", max_length=64)
    merchant_name = models.CharField(u"商户注册名称", max_length=64)
    maintain = models.CharField(u"签约机构", max_length=64)
    maintain_code = models.CharField(u"签约机构号", max_length=64)
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    category = models.CharField(u"分类", max_length=64)
    draw_date = models.CharField(u"提款日期", max_length=64)
    draw_rmb = models.CharField(u"提款金额", max_length=64)
    fee_rmb = models.CharField(u"提款手续费", max_length=64)
    real_rmb = models.CharField(u"实际扣款", max_length=64)
    trans_type = models.CharField(u"交易类型", max_length=64)
    trans_status = models.CharField(u"交易状态", max_length=64)

    class Meta:
        db_table = "lkl_d0"
        verbose_name = verbose_name_plural = u"代理商MPOS个人D0"

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class LKLD1(models.Model):
    """
    数据来源s.lakala.com
    """
    agent = models.CharField(u"当前帐号下级代理商", max_length=64)
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    maintain = models.CharField(u"签约机构", max_length=64)
    maintain_code = models.CharField(u"签约机构号", max_length=64)
    merchant_code = models.CharField(u"商户号", max_length=64)
    merchant_name = models.CharField(u"商户注册名称", max_length=64)
    terminal_num = models.CharField(u"终端号", max_length=64)
    draw_date = models.CharField(u"提款日期", max_length=64)
    draw_rmb = models.CharField(u"提款金额", max_length=64)
    fee_rmb = models.CharField(u"商户手续费", max_length=64)
    card_type = models.CharField(u"卡类型", max_length=64)
    pay_date = models.CharField(u"支付时间", max_length=64)
    pos_type = models.CharField(u"卡应用类型", max_length=64)
    terminal = models.CharField(u"PSAM卡号", max_length=64)

    class Meta:
        db_table = "lkl_d1"
        verbose_name = verbose_name_plural = u"MPOS个人交易明细"

    def __str__(self):
        return self.trans_id
