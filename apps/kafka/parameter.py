# -*- coding:utf-8 _*-
from apps.kafka.models import KafkaBroker, KafkaCluster
from common.utils.common import build_fail_result, get_cc_info_by_ip, is_ip, str_trans_list
from common.utils.monitor_sdk import MonitorExecutor

'''
@summary: 定义不同kafka任务参数处理模块：参数检测，参数提取
@usage:
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
    )
'''


def check_kafka_add_ip(bk_username, ip_list, app_id, app):
    """
       提取公共检测ip的代码来封装，减少重复代码
       @param bk_username: ip在配置平台检测需要的用户名称 参数类型： str
       @param ip_list: 任务中新加的带检测ip列表，参数类型: list
       @param app_id: ip在配置平台检测需要的业务ID 参数类型： int
       @param app: ip的配置平台检测需要的业务名称 参数类型： str
    """
    for node_ip in ip_list:
        if not is_ip(node_ip):
            # 存在非法ip
            return build_fail_result(f"存在非法IP:{node_ip}")
        if KafkaBroker.objects.filter(ip=node_ip).exists():
            # ip已录入平台
            return build_fail_result(f"平台检测到存在该IP:{node_ip}")

        if get_cc_info_by_ip(bk_username=bk_username, app_id=app_id, ip=node_ip)['data']['count'] == 0:
            # 节点不属于对应业务，异常退出
            return build_fail_result(f"节点不属于对应业务{app}，请自查:{node_ip}")

    return None


def retrieval_kafka_deploy_param(post_data, bk_username):
    """
        提取kafka部署参数方法
        @param post_data: 前端post传入的参数信息 参数类型：dict
        @param bk_username: 前端传入的用户名称 参数类型：str
    """

    cluster_name = post_data.get('cluster_name')
    app = post_data.get('app')
    app_id = post_data.get('app_id')
    version = post_data.get('version')
    broker_list = str_trans_list(post_data.get('broker_list'))
    broker_port = int(post_data.get('broker_port'))
    is_create_bk_monitor = int(post_data.get('is_create_bk_monitor'))
    broker_str = ",".join(broker_list)
    description = post_data.get('description')

    if KafkaCluster.objects.filter(cluster_name=cluster_name).exists():
        return build_fail_result(f"集群名称已存在：{cluster_name}")

    if len(broker_list) < 3:
        return build_fail_result(f"集群数量少于3，不满足最小集群标准。目前节点数量：{len(broker_list)}")

    check_result = check_kafka_add_ip(bk_username, broker_list, app_id, app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    return {
        "code": 1,
        "data": {
            "app_id": int(app_id),
            "app": app,
            "add_type": 1,
            "cluster_name": cluster_name,
            "version": version,
            "target_ips": broker_list,
            "broker_str": broker_str,
            "broker_port": broker_port,
            "is_create_bk_monitor": is_create_bk_monitor,
            "kafka_zk_port": 2181,
            "description": description,
            "bk_username": bk_username,
            "task_type": 3
        },
    }


def retrieval_kafka_add_node_param(post_data, bk_username):
    """
       提取kafka broker节点扩容参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    target_ips = str_trans_list(post_data.get('ips'))
    cluster_name = post_data.get('cluster_name')
    cluster = KafkaCluster.objects.get(cluster_name=cluster_name)
    cluster_id = cluster.id
    version = cluster.version
    zk_list = cluster.zk_list
    app_id = cluster.app_id
    app = cluster.app

    if cluster.cluster_status != 3:
        return build_fail_result("集群在非运行中状态下，不能发起集群变更任务，请检测集群当前状态")

    check_result = check_kafka_add_ip(bk_username, target_ips, app_id, app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    return {
        "code": 1,
        "data": {
            "cluster_id": cluster_id,
            "app_id": int(app_id),
            "cluster_name": cluster_name,
            "version": version,
            "target_ips": target_ips,
            "broker_str": zk_list,
            "bk_username": bk_username,
            "task_type": 10
        },
    }


def retrieval_kafka_input_param(post_data, bk_username):
    """
        提取kafka录入参数方法
        @param post_data: 前端post传入的参数信息 参数类型：dict
        @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_name = post_data.get('cluster_name')
    app = post_data.get('app')
    app_id = post_data.get('app_id')
    version_type = post_data.get('version_type')
    version_no = post_data.get('version_no')
    broker_port = post_data.get('broker_port')
    broker_list = str_trans_list(post_data.get('broker_list'))
    topic_list = str_trans_list(post_data.get('topic_list'))
    kafka_zk_list = str_trans_list(post_data.get('kafka_zk_list'))
    kafka_zk_port = post_data.get('kafka_zk_port')
    chroot = post_data.get('chroot')
    is_check_by_zk = int(post_data.get('is_check_by_zk'))
    description = post_data.get('description')
    is_create_bk_monitor = int(post_data.get('is_create_bk_monitor'))

    version = f"{version_type}-{version_no}"
    kafka_zk_str = ",".join(kafka_zk_list)
    zk_url = ''

    if kafka_zk_str == '':
        # 如果kafka_zk信息为空，则给定一个指定值，表面配置为空，方便做逻辑处理
        kafka_zk_str = 'no config zookeeper'
        kafka_zk_port = 0

    if KafkaCluster.objects.filter(cluster_name=cluster_name).exists():
        return build_fail_result(f"集群名称已存在：{cluster_name}")

    check_result = check_kafka_add_ip(bk_username, broker_list, app_id, app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    if is_check_by_zk == 1:
        # 判断是否导出job的执行结果
        is_read_success_message = True
        zk_url = f"{kafka_zk_list[0]}:{kafka_zk_port}"
        if len(broker_list) != 1:
            return build_fail_result(f"选择ZK检测模式broker信息只需要填入一个，请检查输入的broker参数！")
    else:
        is_read_success_message = False

    return {
        "code": 1,
        "data": {
            "app_id": int(app_id),
            "app": app,
            "add_type": 0,
            "cluster_name": cluster_name,
            "version": version,
            "version_type": version_type,
            "version_no": version_no,
            "broker_port": int(broker_port),
            "target_ips": broker_list,
            "topic_list": topic_list,
            "broker_str": kafka_zk_str,
            "kafka_zk_port": kafka_zk_port,
            "zk_url": zk_url,
            "chroot": chroot,
            "is_check_by_zk": is_check_by_zk,
            "is_read_success_message": is_read_success_message,
            "is_create_bk_monitor": is_create_bk_monitor,
            "description": description,
            "bk_username": bk_username,
            "task_type": 9
        },
    }


def retrieval_kafka_install_monitor_param(post_data, bk_username):
    """
        提取kafka添加监控参数方法
        @param post_data: 前端post传入的参数信息 参数类型：dict
        @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_name = post_data.get('cluster_name')
    broker_infos = KafkaBroker.objects.filter(cluster_name=cluster_name).values()
    target_ips = post_data.get('target_ips') if post_data.get('target_ips') \
        else [info.get('ip') for info in broker_infos]
    broker_port = broker_infos[0].get('broker_port')
    cluster = KafkaCluster.objects.get(cluster_name=cluster_name)
    cluster_id = cluster.id
    version = cluster.version
    app_id = cluster.app_id
    bk_data_id = cluster.bk_data_id
    access_token = cluster.access_token
    bk_group_id = cluster.bk_group_id

    if bk_data_id == 0:
        # 如果集群尚未获取到监控平台的data_id,则先去获取专属信息
        monitor_name = f"kafka_{cluster_name}"
        monitor = MonitorExecutor(bk_username)
        bk_data_id, access_token, bk_group_id = monitor.create_monitor_data(app_id, monitor_name)

    # 目前指定kafka exporter 开放端口为29999
    metric_port = 29999

    if not bk_data_id and not access_token:
        return build_fail_result("添加集群监控失败")

    return {
        "code": 1,
        "data": {
            "cluster_id": int(cluster_id),
            "cluster_name": cluster_name,
            "app_id": int(app_id),
            "target_ips": target_ips,
            "bk_data_id": int(bk_data_id),
            "access_token": access_token,
            "metric_port": int(metric_port),
            "bk_group_id": int(bk_group_id),
            "broker_port": int(broker_port),
            "version": version,
            "db_type": 3,
            "bk_username": bk_username,
            "task_type": 12
        },
    }


def retrieval_kafka_destroy_param(post_data, bk_username):
    """
        提取kafka回收参数方法
        @param post_data: 前端post传入的参数信息 参数类型：dict
        @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_name = post_data.get('cluster_name')
    cluster = KafkaCluster.objects.get(cluster_name=cluster_name)
    broker_infos = KafkaBroker.objects.filter(cluster_name=cluster_name).values()
    target_ips = [info.get('ip') for info in broker_infos]
    cluster_id = cluster.id
    bk_group_id = cluster.bk_group_id
    app_id = cluster.app_id
    monitor = MonitorExecutor(bk_username)
    if not monitor.delete_monitor_data(app_id, bk_group_id):
        return build_fail_result("删除集群监控配置失败")
    return {
        "code": 1,
        "data": {
            "cluster_id": int(cluster_id),
            "app_id": int(app_id),
            "cluster_name": cluster_name,
            "target_ips": target_ips,
            "bk_username": bk_username,
            "task_type": 13

        }
    }
