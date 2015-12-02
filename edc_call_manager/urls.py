# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Erik van Widenfelt
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
from django.conf.urls import include, url
from django.contrib import admin
from edc_call_manager.caller_site import site_model_callers

admin.autodiscover()
site_model_callers.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]
