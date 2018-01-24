# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.home, name="user_home"),
    url(r'^news/$', views.news, name="user_news"),
    url(r'^account/$', views.account, name="user_account"),
    url(r'^login/$', views.login, name="user_login"),
    url(r'^register/$', views.register, name="user_register"),
    url(r'^logout/$', views.logout, name="user_logout"),
]
