# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="jk_home"),
    url(r'^login/$', views.home_login, name="jk_home_login"),
    url(r'^info/$', views.info, name="jk_user_info"),
    url(r'^pos_list/$', views.jk_pos_list, name="jk_pos_list"),
    url(r'^pos_detail/$', views.jk_pos_detail, name="jk_pos_detail"),
    url(r'^merchant_prov/$', views.jk_merchant_prov, name="jk_merchant_prov"),
    url(r'^change_merchant_prov/$', views.jk_change_merchant_prov, name="jk_change_merchant_prov"),
    url(r'^friend_list/$', views.friend_list, name="jk_friend_list"),
    url(r'^bind_pos/$', views.bind_pos, name="jk_bind_pos"),
]
