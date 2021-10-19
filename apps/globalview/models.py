# -*- coding: utf-8 -*-
import json

from django.db import models
from django.db.models import Count

from blueapps.utils.logger import logger


'''
@summary: 定义后台管理数据表
@usage:
'''


class TaskRecord(models.Model):
    """
      存储后台执行发布的记录
    """
    DB_TYPE = (
        (1, "ES"),
        (2, "Hadoop"),
        (3, "Kafka")
    )

    TASK_STATUS = (
        (1, "未执行"),
        (2, "正在执行"),
        (3, "执行完成"),
        (4, "执行失败"),
        (5, "任务暂停"),
        (6, "忽略错误"),
        (7, "等待用户"),
        (8, "任务撤销"),
        (9, "状态异常"),
        (10, "步骤强制终止中"),
        (11, "步骤强制终止成功"),
        (12, "步骤强制终止失败"),
    )
    ALERT_STATUS = ((0, "未告警"), (1, "已告警"))
    TASK_TYPE = (
        (0, "其他"),
        (1, "hdfs集群部署"),
        (2, "yarn集群部署"),
        (3, "集群部署"),
        (4, "datanode节点扩容"),
        (5, "datanode节点缩容"),
        (6, "nodemanager节点扩容"),
        (7, "nodemanager节点缩容"),
        (8, "多磁盘扩容"),
        (9, "集群录入检测"),
        (10, "集群扩容"),
        (11, "集群缩容"),
        (12, "监控添加"),
        (13, "集群删除")
    )
    TASK_MODE = ((0, "同步触发"), (1, "异步触发"))

    task_id = models.BigAutoField(primary_key=True, verbose_name="自增列进程id")
    app_id = models.IntegerField(default=0, verbose_name="业务ID")
    pipeline_id = models.CharField(max_length=128, default="sync", db_index=True, verbose_name="pipeline任务id")
    db_type = models.IntegerField(choices=DB_TYPE, default=0, verbose_name="组件类型")
    cluster_name = models.CharField(max_length=256, default="", verbose_name="集群名称")
    task_mode = models.IntegerField(choices=TASK_MODE, default=1, verbose_name="任务模式")
    task_status = models.IntegerField(choices=TASK_STATUS, default=1, verbose_name="结果表任务状态")
    task_type = models.IntegerField(choices=TASK_TYPE, default=0, verbose_name="任务类型")
    op_user = models.CharField(max_length=32, default="unknown", verbose_name="操作者")
    task_kwargs = models.TextField(default="", verbose_name="任务参数")
    pipeline_tree = models.TextField(default="", verbose_name="pipeline_tree")
    alert_status = models.IntegerField(choices=ALERT_STATUS, default=0, verbose_name="告警状态")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="任务创建时间")
    start_time = models.DateTimeField(blank=True, null=True, verbose_name="任务开始时间")
    stop_time = models.DateTimeField(blank=True, null=True, verbose_name="任务结束时间")

    class Meta:
        db_table = "t_task_record"
        verbose_name = "后台任务记录表"
        verbose_name_plural = "后台任务记录表"


def create_record_detail(task_info):
    """
       记录cluster所有的task记录
       @param task_info:{
                "db_type": 1/2/3
                "app_id": app_id,
                "cluster_name": cluster_name,
                "task_type":xxx
                "task_mode:"xxx",
                "pipeline_id":xxx,
                "task_params":task_params,
            }
    """
    task_id = None
    try:
        task_model = TaskRecord.objects.create(
            db_type=task_info['db_type'],
            app_id=task_info['app_id'],
            cluster_name=task_info['cluster_name'],
            task_mode=task_info['task_mode'],
            task_type=task_info['task_type'],
            op_user=task_info['op_user'],
            task_kwargs=json.dumps(task_info['task_params']),
            pipeline_id=task_info['pipeline_id'],
        )
        task_id = task_model.task_id

    except Exception as err:
        logger.error(str(err))

    finally:
        return task_id


def update_record_detail(task_id, update_data):
    """
       根据task_id,更新cluster的task数据
       @param task_id : 任务的主键 ID
       @param update_data: 更新字段参数
    """
    try:

        TaskRecord.objects.filter(task_id=task_id).update(**update_data)
        return True

    except Exception as err:
        logger.error(str(err))
        return False


def update_record_detail_by_pipeline_id(pipeline_id, update_data):
    """
       根据pipeline_id,更新cluster的task数据
       @param pipeline_id : 任务的bamboo流程 ID
       @param update_data : 更新字段参数
    """
    try:

        TaskRecord.objects.filter(pipeline_id=pipeline_id).update(**update_data)
        return True

    except Exception as err:
        logger.error(str(err))
        return False


def get_task_record(pipeline_id):
    """
       通过pipeline_id获取流程任务信息
    """
    try:
        task_params_info = TaskRecord.objects.filter(pipeline_id=pipeline_id).values()
        if task_params_info:

            # 如果存在数据，则只会有一条数据，因为pipeline_id 是唯一的
            return task_params_info[0]
        else:
            return None

    except Exception as err:
        logger.error(str(err))
        return None


def get_task_statistics(app_id_list):
    """
        通过业务列表id返回的分组统计
        @param: app_id_list
    """
    try:
        annotate_query = TaskRecord.objects.filter(
            app_id__in=app_id_list).values('db_type').annotate(
            value=Count('task_id'))

        return [
            {
                "value": query.get("value"),
                "name": f'''{dict(TaskRecord.DB_TYPE).get((query.get("db_type")))}已执行任务数量''',
            }
            for query in annotate_query
        ]

    except Exception as err:
        logger.error(str(err))
        return []
