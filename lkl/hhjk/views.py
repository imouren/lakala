# -*- coding: utf-8 -*-
import json
import logging
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from . import dbutils, utils, models
from prov_code import PROV_CODE

logger = logging.getLogger('statistics')


def hhjk_home(request):
    return HttpResponse(u"华辉金控~")
