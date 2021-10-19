# -*- coding: utf-8 -*-

from django.contrib import admin
from apps.hadoop.models import *


@admin.register(ClusterInfo)
class ClusterInfoAdmin(admin.ModelAdmin):
    pass

