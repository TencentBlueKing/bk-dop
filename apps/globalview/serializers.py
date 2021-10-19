# -*- coding:utf-8 _*-
from rest_framework import serializers
from apps.globalview.models import TaskRecord
'''
@summary:
@usage:
'''


class TaskRecordSerializers(serializers.ModelSerializer):
    db_type = serializers.SerializerMethodField()
    task_status = serializers.SerializerMethodField()
    task_type = serializers.SerializerMethodField()
    alert_status = serializers.SerializerMethodField()
    task_mode = serializers.SerializerMethodField()

    class Meta:
        model = TaskRecord
        fields = "__all__"
        lookup_field = ('db_type', 'cluster_name')

    def get_db_type(self, obj):
        return obj.get_db_type_display()

    def get_task_status(self, obj):
        return obj.get_task_status_display()

    def get_task_type(self, obj):
        return obj.get_task_type_display()

    def get_alert_status(self, obj):
        return obj.get_alert_status_display()

    def get_task_mode(self, obj):
        return obj.get_task_mode_display()
