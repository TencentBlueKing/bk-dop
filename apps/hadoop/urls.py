# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from rest_framework import routers
from apps.hadoop import views


# 注册新的路由地址
router = routers.DefaultRouter()
router.register(r'v1/clusters', views.HadoopClusterViewSet, basename='hadoop_cluster')
router.register(r'v1/detail', views.HadoopDetailViewSet)

# 注册上一级的路由地址并添加
urlpatterns = [
    url(r'^', include(router.urls,)),
]
