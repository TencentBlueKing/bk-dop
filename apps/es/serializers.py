# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.es.models import EsCluster, EsNodeInfo, EsRule


class EsClusterSerializers(serializers.ModelSerializer):
    add_type = serializers.SerializerMethodField()
    cluster_status = serializers.SerializerMethodField()

    class Meta:
        model = EsCluster
        fields = '__all__'

    def get_add_type(self, obj):
        return obj.get_add_type_display()

    def get_cluster_status(self, obj):
        return obj.get_cluster_status_display()


class EsNodeSerializers(serializers.ModelSerializer):
    class Meta:
        model = EsNodeInfo
        fields = '__all__'


class EsRuleSerializers(serializers.ModelSerializer):
    class Meta:
        model = EsRule
        fields = '__all__'
