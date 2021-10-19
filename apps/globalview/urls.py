# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.urls import re_path
from apps.globalview import views
from rest_framework import routers


router = routers.DefaultRouter()
router.register(r'v1/record', views.TaskRecordViewSet, basename='task_list')

urlpatterns = (
    url(r'^$', views.index),
    url(r'^', include(router.urls,)),
    url(r'^v1/apps/$', views.get_app_by_user),
)
