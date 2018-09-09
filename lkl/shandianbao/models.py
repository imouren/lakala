# -*- coding: utf-8 -*-
import uuid
import hashlib
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class SDBTrade(models.Model):
    """
    数据来源https://shandianbao.chinapnr.com/supm/TRD101/index
    交易管理--交易明细查询
    """
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    merchant = models.CharField(u"商户号", max_length=64)
    trade_date = models.CharField(u"交易日期", max_length=64)
    trade_rmb = models.CharField(u"交易金额（元）", max_length=64)
    trade_type = models.CharField(u"交易类型", max_length=64)
    trade_status = models.CharField(u"交易状态", max_length=64)
    card_code = models.CharField(u"卡号", max_length=64)
    card_type = models.CharField(u"卡类型", max_length=64)
    return_code = models.CharField(u"返回码", max_length=64)
    return_desc = models.CharField(u"返回码描述", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64)
    agent_level = models.CharField(u"代理商等级", max_length=64)
    agent = models.CharField(u"代理商号", max_length=64)
    business_type = models.CharField(u"业务类型", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "sdb_trade"
        verbose_name = verbose_name_plural = u"交易明细"
        ordering = ["-trade_date"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class SDBTerminal(models.Model):
    """
    数据来源https://shandianbao.chinapnr.com/supm/TRD101/index
    终端管理--终端明细查询
    """
    terminal = models.CharField(u"终端号", max_length=64, unique=True)
    batch = models.CharField(u"批次号", max_length=64)
    company = models.CharField(u"机具厂商", max_length=64)
    pos_type = models.CharField(u"机具类型", max_length=64)
    pos_version = models.CharField(u"机具型号", max_length=64)
    agent = models.CharField(u"代理商号", max_length=64)
    agent_name = models.CharField(u"代理简称", max_length=64)
    bind_status = models.CharField(u"绑定状态", max_length=64)
    activate_status = models.CharField(u"激活状态", max_length=64)
    bind_merchant = models.CharField(u"绑定商户号", max_length=64)
    bind_time = models.CharField(u"绑定时间", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "sdb_terminal"
        verbose_name = verbose_name_plural = u"终端明细"
        ordering = ["-terminal"]

    def __str__(self):
        return self.terminal


@python_2_unicode_compatible
class SDBToken(models.Model):
    token = models.TextField(u"token")
    is_disabled = models.BooleanField(u"是否禁用", default=False)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "sdb_token"
        verbose_name = verbose_name_plural = u"凭证"
        ordering = ["-create_time"]
