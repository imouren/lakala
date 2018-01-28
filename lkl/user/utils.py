# -*- coding: utf-8 -*-
import string
import random
from django.contrib.auth.models import User
from .models import UserProfile


def get_user_by_code(code, is_phone):
    if is_phone:
        objs = UserProfile.objects.filter(phone=code)
    else:
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


def exists_code(code):

    objs = UserProfile.objects.filter(code=code)
    if objs:
        return True
    else:
        return False


def _generate_code(n):
    res = []
    s = string.letters + string.digits
    for i in range(n):
        letter = random.choice(s)
        res.append(letter)
    return "".join(res)


def generate_code(n=6):
    code = _generate_code(n)
    if exists_code(code):
        return generate_code(n)
    else:
        return code
