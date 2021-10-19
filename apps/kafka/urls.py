from django.conf.urls import include, url

from rest_framework import routers

from apps.kafka import views


# 定义路由地址

# 注册新的路由地址
router = routers.DefaultRouter()
router.register(r'v1/clusters', views.KafkaClusterViewSet, basename='kafka_cluster')
router.register(r'v1/brokers', views.KafkaBrokerViewSet)
router.register(r'v1/topics', views.KafkaTopicViewSet)

# 注册上一级的路由地址并添加
urlpatterns = [
    url(r'^', include(router.urls,)),
]
