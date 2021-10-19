# -*- coding: utf-8 -*-

from django.contrib import admin
from apps.es.models import EsCluster


@admin.register(EsCluster)
class EsClusterAdmin(admin.ModelAdmin):
    pass
