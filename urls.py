# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # 出于安全考虑，默认屏蔽admin访问路径。
    # 开启前请修改路径随机内容，降低被猜测命中几率，提升安全性
    url(r'^iadmin/', admin.site.urls),
    url(r'^account/', include('blueapps.account.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^hadoop/', include('apps.hadoop.urls')),
    url(r'^es/', include('apps.es.urls')),
    url(r'^kafka/', include('apps.kafka.urls')),
    url(r'^', include('apps.globalview.urls')),
]

