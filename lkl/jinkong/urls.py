# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="jk_home"),
    url(r'^info/$', views.info, name="jk_user_info"),
    url(r'^pos_list/$', views.jk_pos_list, name="jk_pos_list"),
    url(r'^pos_detail/$', views.jk_pos_detail, name="jk_pos_detail"),
]
