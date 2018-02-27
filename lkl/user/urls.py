# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views, site

urlpatterns = [
    url(r'^$', views.home, name="user_home"),
    url(r'^info/$', views.info, name="user_info"),
    url(r'^alipay/$', views.alipay, name="user_alipay"),
    url(r'^news/$', views.news, name="user_news"),
    url(r'^account/$', views.account, name="user_account"),
    url(r'^login/$', views.login, name="user_login"),
    url(r'^register/$', views.register, name="user_register"),
    url(r'^logout/$', views.logout, name="user_logout"),
    url(r'^search_terminal/$', views.search_terminal, name="search_terminal"),
    url(r'^bind_pos/$', views.bind_pos, name="bind_pos"),
    url(r'^pos_list/$', views.pos_list, name="pos_list"),
    url(r'^pos_detail/$', views.pos_detail, name="pos_detail"),
    url(r'^friend_list/$', views.friend_list, name="friend_list"),
    # tixian
    url(r'^tixian_rmb/$', views.tixian_rmb, name="tixian_rmb"),
    # wx
    url(r'^wx_redirect/$', views.wx_redirect, name="wx_redirect"),
    # boss
    url(r'^income/$', site.income, name="boss_income"),
]
