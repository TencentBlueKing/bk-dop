# -*- coding: utf-8 -*-
from common.utils.bamboo_flow import BambooFlow


"""
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
    (11, "集群缩容")，
    (12, "添加监控")，
    (13, "集群删除")
"""


def deploy_cluster_flow(deploy_info):
    """
       定义kafka集群部署流程(串行流程)
       @param deploy_info: 部署参数 参数类型:dict
    """
    kafka_deploy_bamboo_flow = BambooFlow(db_type=3, param_info=deploy_info)
    if not kafka_deploy_bamboo_flow.check_param() or not kafka_deploy_bamboo_flow.create_record_detail(task_type=3):
        # 存储任务记录失败，立即退出
        return False
    kafka_deploy_bamboo_flow.add_act(act_name="分发文件", act_component_code="kafka_push_pkg_action")
    kafka_deploy_bamboo_flow.add_act(act_name="部署Kafka集群", act_component_code="install_kafka_action")
    if not kafka_deploy_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def add_node_flow(add_info):
    """
       定义kafka扩容流程(串行流程)
       @param add_info: 扩容参数 参数类型:dict
    """
    kafka_add_node_bamboo_flow = BambooFlow(db_type=3, param_info=add_info)
    if not kafka_add_node_bamboo_flow.check_param() or not \
            kafka_add_node_bamboo_flow.create_record_detail(task_type=10):
        # 存储任务记录失败，立即退出
        return False
    kafka_add_node_bamboo_flow.add_act(act_name="分发文件", act_component_code="kafka_push_pkg_action")
    kafka_add_node_bamboo_flow.add_act(act_name="扩容broker节点", act_component_code="install_kafka_action")
    if not kafka_add_node_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def input_cluster_flow(input_info):
    """
       定义kafka集群录入流程(串行流程)
       @param input_info: 录入参数 参数类型:dict
    """
    kafka_input_bamboo_flow = BambooFlow(db_type=3, param_info=input_info)
    if not kafka_input_bamboo_flow.check_param() or not kafka_input_bamboo_flow.create_record_detail(task_type=9):
        # 存储任务记录失败，立即退出
        return False

    if input_info['is_check_by_zk'] == 1:
        # 表示建立通过zk方式获取kafka集群信息的流程
        kafka_input_bamboo_flow.add_act(act_name="分发python-kazoo模块文件", act_component_code="kazoo_push_pkg_action")
        kafka_input_bamboo_flow.add_act(act_name="添加kazoo模块", act_component_code="install_kazoo_action")
        kafka_input_bamboo_flow.add_act(
            act_name="获取录入的kafka集群信息",
            act_component_code="kafka_input_cluster_for_zk_action")
    else:
        # 表示手动录入broker和topic信息，建立手动录入集群信息的流程
        kafka_input_bamboo_flow.add_act(act_name="检测broker进程是否存在", act_component_code="check_broker_action")

    if not kafka_input_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def install_kafka_cluster_monitor_flow(install_info):
    """
       定义kafka监控添加流程(串行流程)
       @param install_info: 录入参数 参数类型:dict
    """
    kafka_install_monitor_bamboo_flow = BambooFlow(db_type=3, param_info=install_info)
    if not kafka_install_monitor_bamboo_flow.check_param() or not \
            kafka_install_monitor_bamboo_flow.create_record_detail(task_type=12):
        # 存储任务记录失败，立即退出
        return False

    kafka_install_monitor_bamboo_flow.add_act(
        act_name="分发监控组件包",
        act_component_code="push_exporter_action")
    kafka_install_monitor_bamboo_flow.add_act(
        act_name="部署监控脚本并启动",
        act_component_code="install_kafka_monitor_action")
    if not kafka_install_monitor_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def destroy_cluster_flow(destroy_info):
    """
        根据集群名称回收集群信息和监控配置(串行流程)
    """
    kafka_destroy_cluster_bamboo_flow = BambooFlow(db_type=3, param_info=destroy_info)
    if not kafka_destroy_cluster_bamboo_flow.check_param() or not \
            kafka_destroy_cluster_bamboo_flow.create_record_detail(task_type=13):
        # 存储任务记录失败，立即退出
        return False

    kafka_destroy_cluster_bamboo_flow.add_act(
        act_name="删除kafka监控采集任务",
        act_component_code="delete_delete_monitor_action")

    if not kafka_destroy_cluster_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True
