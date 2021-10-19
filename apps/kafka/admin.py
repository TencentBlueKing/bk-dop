# -*- coding: utf-8 -*-
from django.contrib import admin

from apps.kafka.models import KafkaBroker, KafkaCluster, Topic


# Register your models here.


@admin.register(KafkaCluster)
class KafkaClusterAdmin(admin.ModelAdmin):
    pass


@admin.register(KafkaBroker)
class KafkaBrokerAdmin(admin.ModelAdmin):
    pass


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass
