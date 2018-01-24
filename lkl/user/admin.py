# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.template.loader import render_to_string
from easy_select2 import select2_modelform
from suit.admin import SortableTabularInline
from . import models


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "name", "sex", "is_vip", "code", "create_time"]
    fields = ["user", "phone", "name", "sex", "is_vip", "father"]
    search_fields = ["name", "phone"]


admin.site.register(models.UserProfile, UserProfileAdmin)
