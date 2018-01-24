# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from .models import UserProfile


def get_user_by_code(code):
    objs = UserProfile.objects.filter(code=code)
    if objs and len(objs) == 1:
        return objs[0].user
    else:
        return None


def get_user_by_username(username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user
