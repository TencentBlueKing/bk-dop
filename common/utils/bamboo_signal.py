# -*- coding:utf-8 _*-
import json
from datetime import datetime

from apps.es.input_sync_db import sync_db
from apps.es.models import add_es_node, insert_es_cluster, reduce_es_node, update_es_cluster
from apps.globalview.models import TaskRecord, get_task_record, update_record_detail_by_pipeline_id
from apps.hadoop.hadoop_flow import install_hadoop_cluster_monitor_flow
from apps.hadoop.models import (
    create_cluster_info,
    delete_cluster_detail_info,
    insert_cluster_detail_info,
    update_cluster_status,
    update_process_status,
    delete_cluster_info,
)
from apps.hadoop.parameter import retrieval_hadoop_install_monitor_param
from apps.kafka.flow.kafka_flow import install_kafka_cluster_monitor_flow
from apps.kafka.models import (
    add_broker_node,
    delete_kafka_cluster,
    input_cluster_for_zk,
    insert_kafka_cluster,
    update_kafka_cluster, KafkaCluster,
)
from apps.kafka.parameter import retrieval_kafka_install_monitor_param
from blueapps.utils.logger import logger
from common.utils.bamboo_api import PipelineTaskApi


'''
@summary: 接收到bamboo的signal之后做变更处理
@usage:

内部定义的db组件id db_type:
    (1, "ES"),
    (2, "Hadoop"),
    (3, "Kafka")
内部定义的任务流程id task_type:
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
    (13，"集群回收")，

'''


def create_kafka_monitor_for_signal(task_kwargs):
    """
        异步触发创建kafka集群监控任务
    """
    try:
        info = retrieval_kafka_install_monitor_param(
            post_data={"cluster_name": task_kwargs['cluster_name'], "target_ips": task_kwargs['target_ips']},
            bk_username=task_kwargs['bk_username'],)
        if info['code'] == 0:
            # 参数存在异常返回失败
            logger.error("拉起kafka添加监控失败")
            return False

        if not install_kafka_cluster_monitor_flow(info['data']):
            # 分发任务异常
            logger.error("添加kafka监控任务失败")
            return False

    except Exception as err:
        logger.error(f"添加监控任务失败,错误信息:{err}")
        return False


def create_hadoop_monitor_for_signal(task_kwargs):
    """
        异步触发创建hadoop集群监控任务
    """
    try:
        info = retrieval_hadoop_install_monitor_param(
            post_data={"cluster_name": task_kwargs['cluster_name']},
            bk_username=task_kwargs['bk_username'])
        if info['code'] == 0:
            # 参数存在异常返回失败
            logger.error("拉起hadoop添加监控失败")
            return False

        if not install_hadoop_cluster_monitor_flow(info['data']):
            # 分发任务异常
            logger.error("添加hadoop监控任务失败")
            return False

    except Exception as err:
        logger.error(f"添加监控任务失败,错误信息:{err}")
        return False


def change_state_by_signal(node_id, to_state, root_id):
    now_time = datetime.now()
    task_info = get_task_record(root_id)
    if not task_info:
        logger.error("后台记录中任务参数为空")
        return None

    # 节点执行失败
    if to_state == 'FAILED':
        update_record_detail_by_pipeline_id(root_id, {"task_status": 4, "stop_time": now_time})
        change_state_by_task(to_state, task_info, root_id)

    # 流程失败后重试
    if to_state == 'READY':
        update_record_detail_by_pipeline_id(root_id, {"task_status": 2})
        change_state_by_task(to_state, task_info, root_id)

    # 流程被撤销
    elif to_state == 'REVOKED' and node_id == root_id:
        update_record_detail_by_pipeline_id(root_id, {"task_status": 8, "stop_time": now_time})
        change_state_by_task(to_state, task_info, root_id)

    # 流程执行完成
    elif to_state == 'FINISHED' and node_id == root_id:
        update_record_detail_by_pipeline_id(root_id, {"task_status": 3, "stop_time": now_time})
        change_state_by_task(to_state, task_info, root_id)

    # 流程启动时
    elif to_state == 'RUNNING' and node_id == root_id:
        update_record_detail_by_pipeline_id(root_id, {"task_status": 2})
        change_state_by_task(to_state, task_info, root_id)

    # 流程暂停时
    elif to_state == 'SUSPENDED' and node_id == root_id:
        update_record_detail_by_pipeline_id(root_id, {"task_status": 5})
        change_state_by_task(to_state, task_info, root_id)

    # 流程还在运行不做处理
    else:
        return None


def change_state_by_task(state, task_info, root_id):

    task_kwargs = json.loads(task_info['task_kwargs'])
    db_type = task_info['db_type']

    if task_info['task_type'] in [1, 2, 3]:
        # 属于集群部署任务，根据任务的db组件类型，更新对应后端数据
        deploy_task_sync_db(task_kwargs, state, db_type)

    elif task_info['task_type'] in [4, 6, 10]:
        # 属于集群节点扩容类任务，根据任务的db组件类型，更新对应后端数据
        add_node_task_sync_db(task_kwargs, state, db_type)

    elif task_info['task_type'] in [8]:
        # 属于集群磁盘扩容类任务(hdfs专属)，根据任务的db组件类型，更新对应后端数据
        hadoop_add_dir_task_sync_db(task_kwargs, state)

    elif task_info['task_type'] in [5, 7, 11]:
        # 属于集群缩容类任务，根据任务的db组件类型，更新对应后端数据
        remove_task_sync_db(task_kwargs, state, db_type)

    elif task_info['task_type'] in [9]:
        # 属于集群录入类任务，根据任务的db组件类型，更新对应后端数据
        input_task_sync_db(task_kwargs, state, db_type, root_id)

    elif task_info['task_type'] in [12]:
        # 属于集群监控添加类任务，根据任务的db组件类型，更新对应后端数据
        create_monitor_sync_db(task_kwargs, state, db_type)

    elif task_info['task_type'] in [13]:
        # 属于集群回收类任务，根据任务的db组件类型，更新对应后端数据
        destroy_task_sync_db(task_kwargs, state, db_type)

    else:
        logger.error("没有匹配到对应的任务类型，无法更新数据:task_info:{}".format(task_info['task_type']))
        return None


def remove_task_sync_db(task_kwargs, is_state, db_type):
    """
       根据缩容类任务的参数信息和当前状态来同步端口信息
    """
    cluster_id = task_kwargs['cluster_id']
    if is_state in ['RUNNING', 'READY']:
        # 更新集群状态
        update_data = {"cluster_status": 4}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)
            update_process_status(update_data={"process_status": 2}, process_id_list=task_kwargs['process_id_list'])

        elif db_type == 3:
            pass

    elif is_state == 'FINISHED':
        # 更新集群状态
        update_data = {"cluster_status": 3}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)
            # 插入新增的es节点信息
            reduce_es_node(task_kwargs)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)
            # 插入新增的进程信息
            delete_cluster_detail_info(task_kwargs['process_id_list'])

        elif db_type == 3:
            pass

    elif is_state == 'FAILED':
        # 更新集群状态
        update_data = {"cluster_status": 3}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)
            # 插入新增的进程信息
            update_process_status(update_data={"process_status": 0}, process_id_list=task_kwargs['process_id_list'])

        elif db_type == 3:
            pass
    else:
        # 回滚到集群上线状态
        update_data = {"cluster_status": 3}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)

        elif db_type == 3:
            pass


def hadoop_add_dir_task_sync_db(task_kwargs, is_state):
    """
        根据hadoop磁盘扩容类任务的参数信息和当前状态来同步后台信息
    """
    if is_state in ['RUNNING', 'READY']:
        # 更新集群状态
        update_cluster_status(task_kwargs['cluster_id'], {"cluster_status": 4})

    elif is_state == 'FINISHED':
        # 更新集群状态
        update_cluster_status(task_kwargs['cluster_id'], {"cluster_status": 3})
        # 插入新增的目录信息
        update_dir_str = task_kwargs['old_dir_str'] + ',' + ','.join(task_kwargs['scaled_up_dir_list'])
        update_cluster_status(task_kwargs['cluster_id'], {"hdfs_data_dir": update_dir_str})

    else:
        # 回滚到集群上线状态
        update_cluster_status(task_kwargs['cluster_id'], {"cluster_status": 3})


def deploy_task_sync_db(task_kwargs, is_state, db_type):
    """
        根据集群部署类任务的参数和当前状态来同步后台信息
    """
    cluster_id = None
    if is_state == 'FINISHED':
        # 生成集群相关信息
        if db_type == 1:
            cluster_id = insert_es_cluster(task_kwargs)
        elif db_type == 2:
            cluster_id = create_cluster_info(task_kwargs)
            if int(task_kwargs['is_create_bk_monitor']) == 1:
                # 若启动监控添加功能，则拉取添加监控任务。
                create_hadoop_monitor_for_signal(task_kwargs)
        elif db_type == 3:
            cluster_id = insert_kafka_cluster(task_kwargs)
            if int(task_kwargs['is_create_bk_monitor']) == 1:
                # 若启动监控添加功能，则拉取添加监控任务。
                create_kafka_monitor_for_signal(task_kwargs)

        if not cluster_id:
            logger.error(f"部署/录入集群初始化数据失败, 组件类型: {db_type}")
            return False

    return True


def input_task_sync_db(task_kwargs, is_state, db_type, root_id=None):
    """
        根据集群录入类任务的参数和当前状态来同步后台信息
    """
    cluster_id = None
    if is_state == 'FINISHED':
        # 生成集群相关信息
        if db_type == 1:
            # ES 录入
            success_message = None
            pipeline_tree = TaskRecord.objects.get(pipeline_id=root_id).pipeline_tree
            pipeline_tree = json.loads(pipeline_tree)
            for node_id in pipeline_tree:
                success_message = PipelineTaskApi({'node_id': node_id}).get_node_output()
            if success_message:
                cluster_id = sync_db(success_message.get(task_kwargs['target_ip']), task_kwargs)
            else:
                logger.error("该es集群录入检测时，查不到返回的结果")
                return False

        elif db_type == 2:
            # Hadoop 录入
            cluster_id = create_cluster_info(task_kwargs)
            if int(task_kwargs['is_create_bk_monitor']) == 1:
                # 若启动监控添加功能，则拉取添加监控任务。
                create_hadoop_monitor_for_signal(task_kwargs)

        elif db_type == 3:
            # Kafka 录入
            if task_kwargs['is_check_by_zk'] == 0:
                # 手动录入同步信息
                cluster_id = insert_kafka_cluster(task_kwargs)
            else:
                # 通过访问zk获取集群信息后同步数据
                pipeline_tree = TaskRecord.objects.get(pipeline_id=root_id).pipeline_tree
                last_node_id = list((json.loads(pipeline_tree)).keys())[-1]
                success_message = PipelineTaskApi({'node_id': last_node_id}).get_node_output()
                if success_message:
                    cluster_id = input_cluster_for_zk(success_message.get(task_kwargs['target_ips'][0]), task_kwargs)
                else:
                    logger.error("该es集群录入检测时，查不到返回的结果")
                    return False

            if int(task_kwargs['is_create_bk_monitor']) == 1:
                # 若启动监控添加功能，则拉取添加监控任务。
                create_kafka_monitor_for_signal(task_kwargs)

        if not cluster_id:
            logger.error(f"部署/录入集群初始化数据失败, 组件类型: {db_type}")
            return False

    return True


def add_node_task_sync_db(task_kwargs, is_state, db_type):
    """
        根据节点扩容类任务的参数信息和当前状态来同步端口信息
    """
    cluster_id = task_kwargs['cluster_id']
    if is_state in ['RUNNING', 'READY']:
        # 更新集群状态
        update_data = {"cluster_status": 4}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)

        elif db_type == 3:
            update_kafka_cluster(cluster_id, update_data)

    elif is_state == 'FINISHED':
        # 更新集群状态
        update_data = {"cluster_status": 3}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)
            # 插入新增的es节点信息
            add_es_node(task_kwargs)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)
            # 插入新增的进程信息
            insert_cluster_detail_info(task_kwargs)

        elif db_type == 3:
            update_kafka_cluster(cluster_id, update_data)
            # 插入新增的kafka节点信息
            add_broker_node(task_kwargs)
            # 判断是否拉起监控
            if KafkaCluster.objects.get(cluster_name=task_kwargs['cluster_name']).bk_data_id != 0:
                create_kafka_monitor_for_signal(task_kwargs)

    else:
        # 回滚到集群上线状态
        update_data = {"cluster_status": 3}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)

        elif db_type == 3:
            update_kafka_cluster(cluster_id, update_data)


def create_monitor_sync_db(task_kwargs, is_state, db_type):
    """
        根据监控添加类任务的参数信息和当前状态来同步端口信息
    """
    res = False
    if is_state == 'FINISHED':
        # 根据db组件来更新相关信息
        if db_type == 1:
            pass
        elif db_type == 2:
            res = update_cluster_status(
                cluster_id=int(task_kwargs['cluster_id']),
                update_data={
                    'bk_data_id': int(task_kwargs['bk_data_id']),
                    'access_token': task_kwargs['access_token'],
                    'metric_port': int(task_kwargs['metric_port']),
                    'bk_group_id': int(task_kwargs['bk_group_id'])
                })
        elif db_type == 3:
            res = update_kafka_cluster(
                cluster_id=int(task_kwargs['cluster_id']),
                update_data={
                    'bk_data_id': int(task_kwargs['bk_data_id']),
                    'access_token': task_kwargs['access_token'],
                    'metric_port': int(task_kwargs['metric_port']),
                    'bk_group_id': int(task_kwargs['bk_group_id'])
                })

        if not res:
            logger.error(f"更新监控数据失败, 组件类型: {db_type}")
            return False

    return True


def destroy_task_sync_db(task_kwargs, is_state, db_type):
    """
        根据集群回收类任务的参数信息和当前状态来同步端口信息
    """
    res = False
    cluster_id = int(task_kwargs['cluster_id'])
    if is_state in ['RUNNING', 'READY']:
        update_data = {"cluster_status": 8}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)
        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)
        elif db_type == 3:
            # 更新集群状态
            update_kafka_cluster(cluster_id, update_data)

    elif is_state == 'FINISHED':
        # 根据db组件来更新相关信息
        if db_type == 1:
            pass
        elif db_type == 2:
            res = delete_cluster_info(cluster_id=cluster_id)
        elif db_type == 3:
            res = delete_kafka_cluster(task_kwargs['cluster_name'])

        if not res:
            logger.error(f"更新监控数据失败, 组件类型: {db_type}")
            return False

        return True

    else:
        # 回滚到集群上线状态
        update_data = {"cluster_status": 3}
        if db_type == 1:
            update_es_cluster(cluster_id, update_data)

        elif db_type == 2:
            update_cluster_status(cluster_id, update_data)

        elif db_type == 3:
            update_kafka_cluster(cluster_id, update_data)
