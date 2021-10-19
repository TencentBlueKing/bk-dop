# -*- coding: utf-8 -*-
from rest_framework import serializers

from apps.hadoop.models import ClusterDetail, ClusterInfo


class HadoopClusterSerializers(serializers.ModelSerializer):
    add_type = serializers.SerializerMethodField()
    cluster_status = serializers.SerializerMethodField()

    class Meta:
        model = ClusterInfo
        fields = '__all__'

    def get_add_type(self, obj):
        return obj.get_add_type_display()

    def get_cluster_status(self, obj):
        return obj.get_cluster_status_display()


class HadoopDetailSerializers(serializers.ModelSerializer):
    process_status = serializers.SerializerMethodField()

    class Meta:
        model = ClusterDetail
        fields = '__all__'

    def get_process_status(self, obj):
        return obj.get_process_status_display()


