# -*- coding:utf-8 _*-
import json
import os

from apps.kafka.models import KafkaBroker, KafkaCluster, Topic
from blueapps.utils.logger import logger
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.job_sdk import JobExecutor
from config import BASE_DIR


ATOM_DIR = os.path.join(BASE_DIR, 'atoms')

'''
@summary: 定义操作kafka topic 的管理操作
@usage:
'''


def create_topic(post_data, bk_username):
    """
       通过JOB平台调用来创建topic方法，属于同步任务
       @param post_data: 前端传输的参数
       @param bk_username: 操作用户者
    """
    cluster_name = post_data.get('cluster_name')
    topic_name = post_data.get('topic')
    topic_partition_sum = str(post_data.get('topic_partition_sum'))
    topic_replication_factor = str(post_data.get('topic_replication_factor'))
    max_ms = int(post_data.get('max_day')) * 24 * 3600 * 1000
    max_message_byte = int(post_data.get('max_message_MB')) * 1024 * 1024
    max_capacity_byte = int(post_data.get('max_capacity_GB'))
    if max_capacity_byte != -1:
        max_capacity_byte = int(post_data.get('max_capacity_GB')) * 1024 * 1024 * 1024

    if not topic_name:
        logger.error("传入的topic名称为空，请检查")
        return False
    app_id = KafkaCluster.objects.get(cluster_name=cluster_name).app_id
    broker_ip = KafkaBroker.objects.filter(cluster_name=cluster_name).values('ip')[0]['ip']
    broker_url = broker_ip + ":9092"

    client = JobExecutor(bk_username, [broker_ip])
    result, message = client.fast_execute_script({
        "bk_biz_id": app_id,
        "script_content": get_script('kafka_bamboo/components/collections/script_templates/topic_ops.sh'),
        "script_param": get_script_param(
            [broker_url,
             topic_name,
             str(max_ms),
             str(max_capacity_byte),
             str(max_message_byte),
             topic_partition_sum,
             topic_replication_factor]),
        "target_server": {"ip_list": get_job_ip_list([broker_ip])},
        "task_name": f"{cluster_name}集群创建topic:{topic_name}",
    })

    if result and result["data"].get("job_instance").get("status") == 3:
        # 任务执行成功，则更新数据信息，正确返回
        Topic.objects.create(cluster_name=cluster_name, topic=topic_name, create_by=bk_username)
        return True

    # 任务执行失败，则打印错误信息，并异常返回
    logger.error(message)
    return False


def check_topic_param(post_data, bk_username):
    """
       通过JOB平台调用来查看topic的配置信息
       @param post_data: 前端传输的参数
       @param bk_username: 操作用户者
    """
    param_list = []
    cluster_name = post_data.get('cluster_name')
    topic_name = post_data.get('topic')
    if not topic_name:
        logger.error("传入的topic名称为空，请检查")
        return False
    app_id = KafkaCluster.objects.get(cluster_name=cluster_name).app_id
    broker_ip = KafkaBroker.objects.filter(cluster_name=cluster_name).values('ip')[0]['ip']
    broker_url = broker_ip + ":9092"

    client = JobExecutor(bk_username, [broker_ip])
    result, message = client.fast_execute_script({
        "bk_biz_id": app_id,
        "script_content": get_script('kafka_bamboo/components/collections/script_templates/check_topic_param.sh'),
        "script_param": get_script_param(
            [broker_url, topic_name]),
        "target_server": {"ip_list": get_job_ip_list([broker_ip])},
        "task_name": f"查询{cluster_name}集群topic信息",
    })
    if result and result["data"].get("job_instance").get("status") == 3:
        for item in (json.loads(message)).get(broker_ip).splitlines():
            if item.find('All') != -1 or item.find('/etc/profile') != -1:
                continue
            param_list.append({'param_name': item.split('=')[0], 'param_value': item.split('=')[1]})

    return param_list
