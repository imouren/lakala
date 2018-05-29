# -*- coding: utf-8 -*-
import uuid
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible


STATUS_CHOICE = (
    ('UP', u'未支付'),
    ('PD', u'已支付'),
    ('SU', u'成功'),
)


@python_2_unicode_compatible
class XYFToken(models.Model):
    token = models.TextField(u"token")
    is_disabled = models.BooleanField(u"是否禁用", default=False)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "xyf_token"
        verbose_name = verbose_name_plural = u"凭证"
        ordering = ["-create_time"]


@python_2_unicode_compatible
class SYFTrade(models.Model):
    """
    数据来源http://sddl.postar.cn/
    交易管理，当日交易和历史交易
    """
    merchant_name = models.CharField(u"商户名称", max_length=64)
    merchant_receipt = models.CharField(u"商户名称小票号", max_length=64)
    settlement_type = models.CharField(u"交易结算类型", max_length=64)
    account_type = models.CharField(u"到账类型", max_length=64)
    pay_status = models.CharField(u"代付状态", max_length=64)
    agent_code = models.CharField(u"代理商编号", max_length=64)
    agent_name = models.CharField(u"所属代理商", max_length=64)
    pos_type = models.CharField(u"POS机类型", max_length=64)
    yun = models.CharField(u"云闪付", max_length=64)
    site_id = models.CharField(u"网店ID", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64)
    trade_date = models.CharField(u"交易时间", max_length=64)
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    trade_type = models.CharField(u"交易类型", max_length=64)
    consume_type = models.CharField(u"消费类型", max_length=64)
    card_code = models.CharField(u"卡号", max_length=64)
    card_type = models.CharField(u"消费卡类型", max_length=64)
    trade_rmb = models.CharField(u"交易金额（元）", max_length=64)
    trade_fee = models.CharField(u"交易手续费（元）", max_length=64)
    trade_status = models.CharField(u"交易状态", max_length=64)
    trade_card_type = models.CharField(u"卡类型", max_length=64)
    auth_status = models.CharField(u"认证状态", max_length=64)
    card_bank = models.CharField(u"发卡行", max_length=64)
    return_code = models.CharField(u"返回码", max_length=64)
    return_info = models.CharField(u"返回信息", max_length=64)
    flow_status = models.CharField(u"流水状态", max_length=64)

    class Meta:
        db_table = "syf_trade"
        verbose_name = verbose_name_plural = u"交易明细"
        ordering = ["-trade_date"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class SYFTerminal(models.Model):
    """
    数据来源http://sddl.postar.cn/
    交易管理--激活商户管理
    """
    promotion = models.CharField(u"活动名称", max_length=64)
    merchant_receipt = models.CharField(u"商户号", max_length=64)
    merchant_name = models.CharField(u"商户名称", max_length=64)
    agent_code = models.CharField(u"代理商编号", max_length=64)
    agent_name = models.CharField(u"所属代理商", max_length=64)
    sn_code = models.CharField(u"SN号", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64, unique=True)
    bind_date = models.CharField(u"绑定时间", max_length=64)
    recharge_date = models.CharField(u"充值时间", max_length=64)
    recharge_status = models.CharField(u"充值状态", max_length=64)
    trade_rmb = models.CharField(u"活动交易金额（元）", max_length=64)
    ok_status = models.CharField(u"达标状态", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "syf_terminal"
        verbose_name = verbose_name_plural = u"激活商户管理"
        ordering = ["-bind_date"]

    def __str__(self):
        return self.terminal


@python_2_unicode_compatible
class XYFPos(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户")
    sn_code = models.CharField(u"SN号", max_length=64, unique=True)
    terminal = models.CharField(u"终端号", max_length=64, blank=True)
    is_activate = models.BooleanField(u"是否激活", default=False)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def save(self, *args, **kwargs):
        if not self.terminal:
            objs = SYFTerminal.objects.filter(sn_code=self.sn_code)
            if objs:
                obj = objs[0]
                self.terminal = obj.terminal
        return super(XYFPos, self).save(*args, **kwargs)

    class Meta:
        db_table = "xyf_pos"
        verbose_name = verbose_name_plural = u"用户POS机"

    def __str__(self):
        return self.terminal


@python_2_unicode_compatible
class XYFFenRun(models.Model):
    POINT_CHOICE = [
        ("0.515", u"0.515"),
        ("0.520", u"0.520"),
        ("0.525", u"0.525"),
        ("0.530", u"0.530"),
        ("0.535", u"0.535"),
        ("0.540", u"0.540"),
        ("0.545", u"0.545"),
        ("0.550", u"0.550"),
    ]
    user = models.OneToOneField(User, verbose_name=u"用户")
    point = models.CharField(u"提点", choices=POINT_CHOICE, max_length=50)
    message = models.TextField(u"说明", blank=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    class Meta:
        db_table = "xyf_fenrun"
        verbose_name = verbose_name_plural = u"星驿付分润"

    def __str__(self):
        return self.point


@python_2_unicode_compatible
class XYFUserRMB(models.Model):
    """
    用户金钱表
    """
    user = models.OneToOneField(User)
    rmb = models.IntegerField(u"金额(分)")
    is_auto = models.BooleanField(u"自动到账", default=False)
    child_rmb = models.IntegerField(u"推荐金额(分)", default=0)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    class Meta:
        db_table = "xyf_user_rmb"
        verbose_name = verbose_name_plural = u"星用户金钱表"
        ordering = ["-rmb", "-child_rmb"]

    def __str__(self):
        return str(self.rmb)


@python_2_unicode_compatible
class XYFProfit(models.Model):
    """
    用户获利表
    """
    user = models.ForeignKey(User, verbose_name=u"用户")
    fenrun_point = models.CharField(u"提点", max_length=50, blank=True)
    rmb = models.IntegerField(u"利润金额(分)", default=0)
    terminal = models.CharField(u"终端号", max_length=64)
    trade_date = models.CharField(u"交易时间", max_length=64)
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    trade_rmb = models.CharField(u"交易金额（元）", max_length=64)
    trade_fee = models.CharField(u"交易手续费（元）", max_length=64)
    trade_status = models.CharField(u"交易状态", max_length=64)
    trade_card_type = models.CharField(u"卡类型", max_length=64)
    return_code = models.CharField(u"返回码", max_length=64)
    status = models.CharField(u"订单状态", choices=STATUS_CHOICE, max_length=10, default="UP")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    pay_time = models.DateTimeField(u"分红时间", null=True, blank=True)

    class Meta:
        db_table = "xyf_user_profit"
        verbose_name = verbose_name_plural = u"星用户获利表"
        ordering = ["-pay_time"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class XYFTiXianOrder(models.Model):
    ORDER_TYPE_CHOICE = (
        ('RMB', u'返利余额提现'),
        ('CHILD_RMB', u'推荐余额提现'),
    )
    user = models.ForeignKey(User, verbose_name=u"用户")
    user_account = models.CharField(u"用户账号", max_length=512, blank=True)
    rmb = models.IntegerField(u"提现金额(分)")
    fee = models.IntegerField(u"提现手续费(分)")
    status = models.CharField(u"订单状态", choices=STATUS_CHOICE, max_length=10, default="UP")
    order_id = models.CharField(u"订单ID", max_length=64, unique=True)
    order_type = models.CharField(u"提现类型", choices=ORDER_TYPE_CHOICE, max_length=20, default="RMB")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    pay_time = models.DateTimeField(u"提现时间", null=True, blank=True)
    finish_time = models.DateTimeField(u"完结时间", null=True, blank=True)

    def __str__(self):
        return self.order_id

    def save(self, *args, **kwargs):
        if not self.order_id:
            uid = str(uuid.uuid4())
            self.order_id = hashlib.md5(uid).hexdigest()
        return super(XYFTiXianOrder, self).save(*args, **kwargs)

    def _pay_rmb(self):
        return self.rmb - self.fee
    _pay_rmb.short_description = u"到账金额"
    pay_rmb = property(_pay_rmb)

    class Meta:
        db_table = "xyf_tixian_order"
        verbose_name = verbose_name_plural = u"星提现表"
        ordering = ["-pay_time"]
