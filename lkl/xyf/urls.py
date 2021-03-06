# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.home, name="xyf_home"),
    url(r'^login/$', views.home_login, name="xyf_home_login"),
    url(r'^info/$', views.info, name="xyf_user_info"),
    url(r'^pos_list/$', views.xyf_pos_list, name="xyf_pos_list"),
    url(r'^pos_detail/$', views.xyf_pos_detail, name="xyf_pos_detail"),
]
