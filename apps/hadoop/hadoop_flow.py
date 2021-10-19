# -*- coding:utf-8 _*-
from common.utils.bamboo_flow import BambooFlow, BambooSubFlow


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


def sub_init_flow(data):
    """
       定义子流程，构建目标节点初始化过程，作为公共流程。适用于部署和扩容流程过程。
       @param data: 子流程参数 参数类型: dict
    """
    sub_bamboo_flow = BambooSubFlow(db_type=2, param_info=data)
    sub_bamboo_flow.add_act(act_name="hadoop集群新节点安装包分发过程",
                            act_component_code="package_distribute_action",)
    sub_bamboo_flow.add_act(act_name="hadoop集群新节点初始化过程",
                            act_component_code="init_before_deploy_action", )
    sub_bamboo_flow.add_act(act_name="hadoop集群同步域名解析过程",
                            act_component_code="sync_dns_config_action", )
    sub_bamboo_flow.add_act(act_name="集群内部节点同步推送用户公钥过程",
                            act_component_code="push_node_rsa_action", )
    sub_bamboo_flow.add_act(act_name="集群建立用户免认证过程",
                            act_component_code="create_auth_free_login_action", )
    sub_bamboo_flow.add_act(act_name="测试集群内部免认证是否正常",
                            act_component_code="check_free_login_action", )
    sub_bamboo_flow.add_act(act_name="hadoop集群新节点推送配置过程",
                            act_component_code="push_config_action", )

    return sub_bamboo_flow.build_sub_bamboo()


def deploy_cluster_flow(deploy_info):
    """
       定义hadoop集群部署流程(串行流程)
       @param deploy_info: 缩容参数 参数类型:dict
    """
    sub_act, act_tree = sub_init_flow(data=deploy_info)
    hadoop_deploy_bamboo_flow = BambooFlow(db_type=2, param_info=deploy_info)
    if not hadoop_deploy_bamboo_flow.check_param() or not hadoop_deploy_bamboo_flow.create_record_detail(task_type=3):
        # 存储任务记录失败，立即退出
        return False
    hadoop_deploy_bamboo_flow.add_sub(sub_flow=sub_act, act_tree=act_tree)
    hadoop_deploy_bamboo_flow.add_act(act_name="启动zookeeper集群过程",
                                      act_component_code="start_zk_server_action",)
    hadoop_deploy_bamboo_flow.add_act(act_name="启动Journal集群过程",
                                      act_component_code="ops_node_action",
                                      private_list=[
                                          {'name': 'node_name', 'value': 'journalnode'},
                                          {'name': 'ops', 'value': 'start'}
                                      ])
    hadoop_deploy_bamboo_flow.add_act(act_name="启动NameNode节点过程",
                                      act_component_code="start_name_node_action",
                                      private_list=[{'name': 'node_name', 'value': 'namenode'}])
    hadoop_deploy_bamboo_flow.add_act(act_name="启动StandbyNameNode节点过程",
                                      act_component_code="start_name_node_action",
                                      private_list=[{'name': 'node_name', 'value': 'standbynamenode'}])
    hadoop_deploy_bamboo_flow.add_act(act_name="启动DataNode节点过程",
                                      act_component_code="ops_node_action",
                                      private_list=[
                                          {'name': 'node_name', 'value': 'datanode'},
                                          {'name': 'ops', 'value': 'start'}
                                      ])
    # 如果ops_type为hdfs_yarn ，则引入yarn部署流程
    if deploy_info['ops_type'] == 'hdfs_yarn':

        hadoop_deploy_bamboo_flow.add_act(act_name="启动ResourceManager集群过程",
                                          act_component_code="start_yarn_node_action",
                                          private_list=[
                                              {'name': 'node_name', 'value': 'resourcemanager'},
                                              {'name': 'ops', 'value': 'start'}
                                          ])

        hadoop_deploy_bamboo_flow.add_act(act_name="启动NodeManager集群过程",
                                          act_component_code="start_yarn_node_action",
                                          private_list=[
                                              {'name': 'node_name', 'value': 'nodemanager'},
                                              {'name': 'ops', 'value': 'start'}
                                          ])

    if not hadoop_deploy_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def add_datanode_flow(expand_info):
    """
       定义hadoop节点扩容(datanode)流程(串行流程)
       @param expand_info: 扩容参数
    """
    sub_act, act_tree = sub_init_flow(data=expand_info)
    hadoop_add_node_bamboo_flow = BambooFlow(db_type=2, param_info=expand_info)
    if not hadoop_add_node_bamboo_flow.check_param() or not hadoop_add_node_bamboo_flow.create_record_detail(
            task_type=4):
        # 存储任务记录失败，立即退出
        return False
    hadoop_add_node_bamboo_flow.add_sub(sub_flow=sub_act, act_tree=act_tree)
    hadoop_add_node_bamboo_flow.add_act(act_name="增加hadoop集群白名单过程",
                                        act_component_code="add_include_config_action",)

    hadoop_add_node_bamboo_flow.add_act(act_name="启动DataNode节点过程",
                                        act_component_code="ops_node_action",
                                        private_list=[
                                            {'name': 'node_name', 'value': 'datanode'},
                                            {'name': 'ops', 'value': 'start'}
                                        ])

    if not hadoop_add_node_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def add_dir_flow(expand_info):
    """
       定义hadoop目录扩容流程(串行流程)
       @param expand_info: 扩容参数
    """
    hadoop_add_dir_bamboo_flow = BambooFlow(db_type=2, param_info=expand_info)
    if not hadoop_add_dir_bamboo_flow.check_param() or not hadoop_add_dir_bamboo_flow.create_record_detail(task_type=8):
        # 存储任务记录失败，立即退出
        return False

    hadoop_add_dir_bamboo_flow.add_act(act_name="检测新加目录是否符合规范",
                                       act_component_code="check_add_dir_action",)
    hadoop_add_dir_bamboo_flow.add_act(act_name="刷新存储数据目录配置过程",
                                       act_component_code="datanode_re_config_dir_action",)

    if not hadoop_add_dir_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def remove_datanode_flow(remove_info):
    """
       定义hadoop节点缩容(datanode)流程(串行流程)
       @param remove_info: 缩容参数
    """
    hadoop_remove_node_bamboo_flow = BambooFlow(db_type=2, param_info=remove_info)
    if not hadoop_remove_node_bamboo_flow.check_param() or not hadoop_remove_node_bamboo_flow.create_record_detail(
            task_type=5):
        # 存储任务记录失败，立即退出
        return False
    hadoop_remove_node_bamboo_flow.add_act(act_name="增加hadoop集群黑名单过程",
                                           act_component_code="remove_datanode_config_action", )
    hadoop_remove_node_bamboo_flow.add_act(act_name="关闭DataNode节点过程",
                                           act_component_code="ops_node_action",
                                           private_list=[
                                               {'name': 'node_name', 'value': 'datanode'},
                                               {'name': 'ops', 'value': 'stop'}
                                           ])

    if not hadoop_remove_node_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def input_cluster_flow(input_info):
    """
       定义hadoop集群录入流程(串行流程)
       @param input_info: 缩容参数 参数类型:dict
    """
    hadoop_input_bamboo_flow = BambooFlow(db_type=2, param_info=input_info)
    if not hadoop_input_bamboo_flow.check_param() or not hadoop_input_bamboo_flow.create_record_detail(task_type=9):
        # 存储任务记录失败，立即退出
        return False

    for node_name in ['namenode', 'standbynamenode', 'datanode', 'journalnode']:

        if len(input_info[node_name]) == 0:
            continue

        hadoop_input_bamboo_flow.add_act(act_name=f"检测{node_name}节点",
                                         act_component_code="check_node_action",
                                         private_list=[{'name': 'node_name', 'value': node_name}])

    if len(input_info['resourcemanager']) != 0:
        hadoop_input_bamboo_flow.add_act(act_name=f"检测resourcemanager节点",
                                         act_component_code="check_node_action",
                                         private_list=[{'name': 'node_name', 'value': 'resourcemanager'}])

    if len(input_info['nodemanager']) != 0:
        hadoop_input_bamboo_flow.add_act(act_name=f"检测nodemanager节点",
                                         act_component_code="check_node_action",
                                         private_list=[{'name': 'node_name', 'value': 'nodemanager'}])

    if not hadoop_input_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def install_hadoop_cluster_monitor_flow(monitor_info):
    """
       定义hadoop监控添加流程(串行流程)
       @param monitor_info: 缩容参数 参数类型:dict
    """
    hadoop_install_monitor_bamboo_flow = BambooFlow(db_type=2, param_info=monitor_info)
    if not hadoop_install_monitor_bamboo_flow.check_param() or not \
            hadoop_install_monitor_bamboo_flow.create_record_detail(task_type=12):
        # 存储任务记录失败，立即退出
        return False

    hadoop_install_monitor_bamboo_flow.add_act(
        act_name="分发监控组件包",
        act_component_code="push_exporter_action")
    hadoop_install_monitor_bamboo_flow.add_act(
        act_name="部署监控脚本并启动",
        act_component_code="install_hadoop_monitor_action")
    if not hadoop_install_monitor_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True


def destroy_cluster_flow(destroy_info):
    """
        根据集群名称回收集群信息和监控配置(串行流程)
    """
    hadoop_destroy_cluster_bamboo_flow = BambooFlow(db_type=2, param_info=destroy_info)
    if not hadoop_destroy_cluster_bamboo_flow.check_param() or not \
            hadoop_destroy_cluster_bamboo_flow.create_record_detail(task_type=13):
        # 存储任务记录失败，立即退出
        return False

    hadoop_destroy_cluster_bamboo_flow.add_act(
        act_name="删除hadoop监控采集任务",
        act_component_code="hadoop_delete_monitor_action")

    if not hadoop_destroy_cluster_bamboo_flow.build_bamboo():
        # 返回false证明建立流程任务失败，异常退出
        return False

    return True
