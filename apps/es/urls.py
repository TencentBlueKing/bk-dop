# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from rest_framework import routers

from apps.es import views

# 注册新的路由地址
router = routers.DefaultRouter()
router.register(r'v1/clusters', views.EsClusterViewSet, basename='es_cluster')
router.register(r'v1/rules', views.EsRuleViewSet)
router.register(r'v1/nodes', views.EsNodeViewSet)

# 注册上一级的路由地址并添加
urlpatterns = [
    url(r'^', include(router.urls, )),
    # url(r'kibana/(?P<cluster>\w+)/(?P<path>.*)', views.kibana_view),
    url(r'cerebro/(?P<cluster>\w+)/(?P<path>.*)', views.cerebro_view),
]
