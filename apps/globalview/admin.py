# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.globalview.models import TaskRecord


@admin.register(TaskRecord)
class EsClusterAdmin(admin.ModelAdmin):
    pass
