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
class JKMerchant(models.Model):
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
        db_table = "jk_merchant"
        verbose_name = verbose_name_plural = u"商户信息"
        ordering = ["-create_time"]

    def __str__(self):
        return self.merchant_code


@python_2_unicode_compatible
class JKTrade(models.Model):
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
        db_table = "jk_trade"
        verbose_name = verbose_name_plural = u"交易明细"
        ordering = ["-trade_date"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class JKTerminal(models.Model):
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
        db_table = "jk_terminal"
        verbose_name = verbose_name_plural = u"终端设备"
        ordering = ["-storage_date"]

    def __str__(self):
        return self.sn_code


@python_2_unicode_compatible
class JKSettlement(models.Model):
    """
    数据来源http://119.18.194.36/
    minipos商户结算单查询
    """
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    merchant_code = models.CharField(u"商户编号", max_length=64)
    register_name = models.CharField(u"注册名称", max_length=64)
    start_time = models.CharField(u"发起时间", max_length=64)
    trade_rmb = models.CharField(u"金额（元）", max_length=64)
    trade_fee = models.CharField(u"手续费（元）", max_length=64)
    pay_type = models.CharField(u"付款方式", max_length=64)
    end_time = models.CharField(u"完成时间", max_length=64)
    pay_status = models.CharField(u"结算状态", max_length=64)
    fenrun = models.CharField(u"分润", max_length=64)
    update_time = models.DateTimeField(u"爬取更新时间", auto_now=True)

    class Meta:
        db_table = "jk_settlement"
        verbose_name = verbose_name_plural = u"商户结算单查询"
        ordering = ["-update_time"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class JKToken(models.Model):
    token = models.TextField(u"token")
    is_disabled = models.BooleanField(u"是否禁用", default=False)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = "jk_token"
        verbose_name = verbose_name_plural = u"凭证"
        ordering = ["-create_time"]


@python_2_unicode_compatible
class JKPos(models.Model):
    user = models.ForeignKey(User, verbose_name=u"用户")
    sn_code = models.CharField(u"SN号", max_length=64, unique=True)
    terminal = models.CharField(u"终端号", max_length=64, blank=True)
    is_activate = models.BooleanField(u"是否激活", default=False)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    def save(self, *args, **kwargs):
        if not self.terminal:
            objs = JKTerminal.objects.filter(sn_code=self.sn_code)
            if objs:
                obj = objs[0]
                self.terminal = obj.terminal
        return super(JKPos, self).save(*args, **kwargs)

    class Meta:
        db_table = "jk_pos"
        verbose_name = verbose_name_plural = u"用户POS机"

    def __str__(self):
        return self.sn_code


@python_2_unicode_compatible
class JKFenRun(models.Model):
    POINT_CHOICE = [
        ("0.520", u"0.520"),
        ("0.525", u"0.525"),
        ("0.530", u"0.530"),
        ("0.535", u"0.535"),
        ("0.540", u"0.540"),
        ("0.545", u"0.545"),
        ("0.550", u"0.550"),
        ("0.555", u"0.555"),
        ("0.560", u"0.560"),
        ("0.565", u"0.565"),
        ("0.570", u"0.570"),
        ("0.575", u"0.575"),
        ("0.580", u"0.580"),
        ("0.585", u"0.585"),
        ("0.590", u"0.590"),
        ("0.595", u"0.595"),
        ("0.60", u"0.60"),
    ]
    user = models.OneToOneField(User, verbose_name=u"用户")
    point = models.CharField(u"提点", choices=POINT_CHOICE, max_length=50)
    message = models.TextField(u"说明", blank=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    class Meta:
        db_table = "jk_fenrun"
        verbose_name = verbose_name_plural = u"金控分润"

    def __str__(self):
        return self.point


@python_2_unicode_compatible
class JKYunFenRun(models.Model):
    POINT_CHOICE = [
        ("0.28", u"0.28"),
        ("0.29", u"0.29"),
        ("0.30", u"0.30"),
        ("0.31", u"0.31"),
        ("0.32", u"0.32"),
        ("0.33", u"0.33"),
        ("0.34", u"0.34"),
        ("0.35", u"0.35"),
        ("0.36", u"0.36"),
        ("0.37", u"0.37"),
        ("0.38", u"0.38"),
    ]
    user = models.OneToOneField(User, verbose_name=u"用户")
    point = models.CharField(u"提点", choices=POINT_CHOICE, max_length=50)
    message = models.TextField(u"说明", blank=True)
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    update_time = models.DateTimeField(u"更新时间", auto_now=True)

    class Meta:
        db_table = "jk_yunfenrun"
        verbose_name = verbose_name_plural = u"金控云闪付分润"

    def __str__(self):
        return self.point


@python_2_unicode_compatible
class JKUserRMB(models.Model):
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
        db_table = "jk_user_rmb"
        verbose_name = verbose_name_plural = u"金用户金钱表"
        ordering = ["-rmb", "-child_rmb"]

    def __str__(self):
        return str(self.rmb)


@python_2_unicode_compatible
class JKProfit(models.Model):
    """
    用户获利表
    """
    user = models.ForeignKey(User, verbose_name=u"用户")
    fenrun_point = models.CharField(u"提点", max_length=50, blank=True)
    rmb = models.IntegerField(u"利润金额(分)", default=0)
    # copy
    merchant_code = models.CharField(u"商户编号", max_length=64)
    terminal = models.CharField(u"终端号", max_length=64)
    trade_date = models.CharField(u"交易日期", max_length=64)
    trade_rmb = models.CharField(u"交易金额（元）", max_length=64)
    trade_status = models.CharField(u"交易状态", max_length=64)
    return_code = models.CharField(u"应答码", max_length=64)
    card_type = models.CharField(u"卡类型", max_length=64)
    trade_fee = models.CharField(u"交易手续费（元）", max_length=64)
    qingfen_rmb = models.CharField(u"清分金额", max_length=64)
    trans_id = models.CharField(u"流水号", max_length=64, unique=True)
    fenrun = models.CharField(u"分润", max_length=64)
    trade_category = models.CharField(u"交易类别", max_length=64)
    product = models.CharField(u"产品标识", max_length=64)
    # 状态和时间
    status = models.CharField(u"订单状态", choices=STATUS_CHOICE, max_length=10, default="UP")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    pay_time = models.DateTimeField(u"分红时间", null=True, blank=True)

    class Meta:
        db_table = "jk_user_profit"
        verbose_name = verbose_name_plural = u"金用户获利表"
        ordering = ["-pay_time"]

    def __str__(self):
        return self.trans_id


@python_2_unicode_compatible
class JKTiXianOrder(models.Model):
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
        return super(JKTiXianOrder, self).save(*args, **kwargs)

    def _pay_rmb(self):
        return self.rmb - self.fee
    _pay_rmb.short_description = u"到账金额"
    pay_rmb = property(_pay_rmb)

    class Meta:
        db_table = "jk_tixian_order"
        verbose_name = verbose_name_plural = u"金提现表"
        ordering = ["-pay_time"]
