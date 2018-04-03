# -*- coding: utf-8 -*-
import re
from django import forms
from django.contrib.auth import forms as django_forms
from django.http.request import HttpRequest
from django.urls import reverse
from easy_select2 import select2_modelform, apply_select2
from captcha.fields import CaptchaField
from django.contrib import auth
from . import utils, dbutils
from . import models


