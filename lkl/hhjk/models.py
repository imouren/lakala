# -*- coding: utf-8 -*-
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class HHJKMerchant(models.Model):
    """
    数据来源http://119.18.194.36/
    minipos商户信息查询
    """
    merchant_code = models.CharField(u"商户编号", max_length=64, unique=True)
    merchant_name = models.CharField(u"商户名称", max_length=64)
    phone = models.CharField(u"手机", max_length=64)
    agent_name = models.CharField(u"直属机构", max_length=64)
    merchant_type = models.CharField(u"商户类型", max_length=64)
    create_time = models.CharField(u"创建时间", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "hhjk_merchant"
        verbose_name = verbose_name_plural = u"商户信息"
        ordering = ["-create_time"]

    def __str__(self):
        return self.merchant_code


@python_2_unicode_compatible
class HHJKTrade(models.Model):
    """
    数据来源http://119.18.194.36/
    minipos商户交易明细查询
    """
    merchant_code = models.CharField(u"商户编号", max_length=64)
    register_name = models.CharField(u"注册名称", max_length=64)
    agent_name = models.CharField(u"所属机构", max_length=64)
    phone = models.CharField(u"手机", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64)
    trade_date = models.CharField(u"交易日期", max_length=64)
    trade_time = models.CharField(u"交易时间", max_length=64)
    trade_rmb = models.CharField(u"交易金额（元）", max_length=64)
    trade_type = models.CharField(u"交易类型", max_length=64)
    trade_status = models.CharField(u"交易状态", max_length=64)
    is_miao = models.CharField(u"是否秒到", max_length=64)
    return_code = models.CharField(u"应答码", max_length=64)
    card_type = models.CharField(u"卡类型", max_length=64)
    card_code = models.CharField(u"卡号", max_length=64)
    card_bank = models.CharField(u"发卡行", max_length=64)
    trade_fee = models.CharField(u"交易手续费（元）", max_length=64)
    qingfen_rmb = models.CharField(u"清分金额", max_length=64)
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    fenrun = models.CharField(u"分润", max_length=64)
    trade_category = models.CharField(u"交易类别", max_length=64)
    product = models.CharField(u"产品标识", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "hhjk_trade"
        verbose_name = verbose_name_plural = u"交易明细"
        ordering = ["-trade_date"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class HHJKTerminal(models.Model):
    """
    数据来源http://119.18.194.36/
    终端设备管理--终端设备查询
    """
    factory = models.CharField(u"厂商", max_length=64)
    merchant_code = models.CharField(u"商户编号", max_length=64)
    agent_code = models.CharField(u"机构编号", max_length=64)
    pos_type = models.CharField(u"型号", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64)
    communication = models.CharField(u"通讯方式", max_length=64)
    sn_code = models.CharField(u"序列号", max_length=64, unique=True)
    storage_date = models.CharField(u"入库时间", max_length=64)
    install_date = models.CharField(u"安装时间", max_length=64)
    is_xjrw = models.CharField(u"携机入网", max_length=64)
    business = models.CharField(u"业务模式", max_length=64)
    fee_receive = models.CharField(u"服务费收取", max_length=64)
    fee_back = models.CharField(u"服务费返还", max_length=64)
    status = models.CharField(u"状态", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "hhjk_terminal"
        verbose_name = verbose_name_plural = u"终端设备"
        ordering = ["-storage_date"]

    def __str__(self):
        return self.sn_code


@python_2_unicode_compatible
class HHJKToken(models.Model):
    token = models.TextField(u"token")
    is_disabled = models.BooleanField(u"是否禁用", default=False)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "hhjk_token"
        verbose_name = verbose_name_plural = u"凭证"
        ordering = ["-create_time"]
