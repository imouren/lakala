# -*- coding: utf-8 -*-
import uuid
import hashlib
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible


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
    consume_type = models.CharField(u"交易类型", max_length=64)
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

    def __str__(self):
        return self.terminal
