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
    (11, "集群缩容")
"""


def deploy_cluster_flow(deploy_info):
    """
       定义es集群部署流程(串行流程)
       @param deploy_info: 部署参数 参数类型:dict
    """
    es_deploy_bamboo_flow = BambooFlow(db_type=1, param_info=deploy_info)
    if not es_deploy_bamboo_flow.check_param() or not es_deploy_bamboo_flow.create_record_detail(task_type=3):
        # 存储任务记录失败，立即退出
        return False

    es_deploy_bamboo_flow.add_act(act_name="分发文件",
                                  act_component_code="es_push_pkg_action",
                                  private_list=[{'name': 'target_ips', 'value': deploy_info['master_list'] +
                                                 deploy_info['data_list']
                                                 + deploy_info['cold_list']
                                                 + deploy_info['client_list']}])
    if deploy_info['spec'] == 'mixed':
        es_deploy_bamboo_flow.add_act(act_name="部署master节点",
                                      act_component_code="install_es_action",
                                      private_list=[{'name': 'role', 'value': 'all'}])
    elif deploy_info['spec'] == 'dedicated':
        es_deploy_bamboo_flow.add_act(act_name="部署master节点",
                                      act_component_code="install_es_action",
                                      private_list=[{'name': 'role', 'value': 'master'}])

        es_deploy_bamboo_flow.add_act(act_name="部署data节点",
                                      act_component_code="install_es_action",
                                      private_list=[{'name': 'role', 'value': 'data'}])

        if len(deploy_info['cold_list']) != 0:
            es_deploy_bamboo_flow.add_act(act_name="部署cold节点",
                                          act_component_code="install_es_action",
                                          private_list=[{'name': 'role', 'value': 'cold'}])
        if len(deploy_info['client_list']) != 0:
            es_deploy_bamboo_flow.add_act(act_name="部署client节点",
                                          act_component_code="install_es_action",
                                          private_list=[{'name': 'role', 'value': 'client'}])

    if deploy_info['version'] == "5.4.0":
        es_deploy_bamboo_flow.add_act(act_name="初始化权限", act_component_code="search_guard_init_action")

    es_deploy_bamboo_flow.add_act(act_name="账号密码设置", act_component_code="es_grant_action")

    if not es_deploy_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def add_node_flow(add_info):
    """
       定义es集群节点扩容流程(串行流程)
       @param add_info: 扩容参数 参数类型:dict
    """
    es_add_bamboo_flow = BambooFlow(db_type=1, param_info=add_info)
    if not es_add_bamboo_flow.check_param() or not es_add_bamboo_flow.create_record_detail(task_type=10):
        # 存储任务记录失败，立即退出
        return False
    es_add_bamboo_flow.add_act(act_name="分发文件",
                               act_component_code="es_push_pkg_action",
                               private_list=[{'name': 'target_ips', 'value': add_info[f"{add_info['role']}_list"]}])

    es_add_bamboo_flow.add_act(act_name=f"扩容{add_info['role']}节点",
                               act_component_code="install_es_action",
                               private_list=[{'name': 'role', 'value': add_info['role']}])

    if not es_add_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def reduce_node_flow(reduce_info):
    """
       定义es集群节点缩容流程(串行流程)
       @param reduce_info: 缩容参数 参数类型:dict
    """
    es_reduce_bamboo_flow = BambooFlow(db_type=1, param_info=reduce_info)
    if not es_reduce_bamboo_flow.check_param() or not es_reduce_bamboo_flow.create_record_detail(task_type=11):
        # 存储任务记录失败，立即退出
        return False
    es_reduce_bamboo_flow.add_act(act_name="缩容节点", act_component_code="es_node_reduce_action")
    if not es_reduce_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def input_cluster_flow(input_info):
    """
       定义es集群录入流程(串行流程)
       @param input_info: 缩容参数 参数类型:dict
    """
    es_input_bamboo_flow = BambooFlow(db_type=1, param_info=input_info)
    if not es_input_bamboo_flow.check_param() or not es_input_bamboo_flow.create_record_detail(task_type=9):
        # 存储任务记录失败，立即退出
        return False

    es_input_bamboo_flow.add_act(
        act_name=f"导入集群{input_info['cluster_name']}",
        act_component_code="es_input_cluster_action")

    if not es_input_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True
