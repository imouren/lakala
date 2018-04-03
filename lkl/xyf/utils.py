# -*- coding: utf-8 -*-
import redis
import string
import random
import time
from collections import defaultdict
from decimal import Decimal
from django.contrib.auth.models import User
from django.conf import settings
from .models import UserProfile, LKLTrade01, UserPos, LKLD1, UserAlipay
from lkl import config


rclient = redis.Redis(**config.REDIS_DATA)


