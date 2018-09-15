# -*- coding: utf-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.hhjk_home, name="hhjk_home"),
    url(r'^area/$', views.hhjk_area, name="hhjk_area"),
    url(r'^area/change/$', views.hhjk_area_change, name="hhjk_area_change"),
]
