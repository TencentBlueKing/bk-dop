# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.kafka.models import KafkaBroker, KafkaCluster, Topic


class KafkaClusterSerializers(serializers.ModelSerializer):
    add_type = serializers.SerializerMethodField()
    cluster_status = serializers.SerializerMethodField()

    class Meta:
        model = KafkaCluster
        fields = "__all__"

    def get_add_type(self, obj):
        return obj.get_add_type_display()

    def get_cluster_status(self, obj):
        return obj.get_cluster_status_display()


class TopicSerializers(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class KafkaBrokerSerializers(serializers.ModelSerializer):
    class Meta:
        model = KafkaBroker
        fields = "__all__"
