# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views, site

urlpatterns = [
    url(r'^$', views.home, name="user_home"),
    url(r'^home_login/$', views.home_login, name="user_home_login"),
    url(r'^info/$', views.info, name="user_info"),
    url(r'^alipay/$', views.alipay, name="user_alipay"),
    url(r'^news/$', views.news, name="user_news"),
    url(r'^account/$', views.account, name="user_account"),
    # user
    url(r'^login/$', views.login, name="user_login"),
    url(r'^register/$', views.register, name="user_register"),
    url(r'^logout/$', views.logout, name="user_logout"),
    url(r'^password_reset/$', views.password_reset, name="password_reset"),
    # pos and friends
    url(r'^search_terminal/$', views.search_terminal, name="search_terminal"),
    url(r'^bind_pos/$', views.bind_pos, name="bind_pos"),
    url(r'^pos_list/$', views.pos_list, name="pos_list"),
    url(r'^pos_detail/$', views.pos_detail, name="pos_detail"),
    url(r'^friend_list/$', views.friend_list, name="friend_list"),
    # tixian
    url(r'^tixian_rmb/$', views.tixian_rmb, name="tixian_rmb"),
    url(r'^tixian_child_rmb/$', views.tixian_child_rmb, name="tixian_child_rmb"),
    url(r'^tixian_list/$', views.tixian_list, name="tixian_list"),
    # set fenrun
    url(r'^set_fenrun/(?P<child>[0-9]{11})/$', views.set_fenrun, name="set_fenrun"),
    # wx
    url(r'^bind_wx_page/$', views.bind_wx_page, name="bind_wx_page"),
    url(r'^bind_wx/$', views.bind_wx, name="bind_wx"),
    url(r'^wx_redirect/$', views.wx_redirect, name="wx_redirect"),
    url(r'^wx_redirect_login/$', views.wx_redirect_login, name="wx_redirect_login"),
    # admin
    url(r'^income/$', site.income, name="admin_income"),
    url(r'^reminder/$', site.reminder, name="admin_reminder"),
    url(r'^jk_income/$', site.jk_income, name="admin_jk_income"),
]
