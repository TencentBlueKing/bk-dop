# -*- coding:utf-8 _*-
from apps.es.models import EsCluster, EsNodeInfo
from common.utils.common import build_fail_result, get_cc_info_by_ip, is_ip, str_trans_list


'''
@summary: 定义不同ES任务参数处理模块：参数检测，参数提取
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


def check_es_add_ip(bk_username, ip_list, app_id, app):
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
        if EsNodeInfo.objects.filter(ip=node_ip).exists():
            # ip已录入平台
            return build_fail_result(f"平台检测到存在该IP:{node_ip}")

        if get_cc_info_by_ip(bk_username=bk_username, app_id=app_id, ip=node_ip)['data']['count'] == 0:
            # 节点不属于对应业务，异常退出

            return build_fail_result(f"节点不属于对应业务{app}，请自查:{node_ip}")

    return None


def retrieval_es_deploy_param(post_data, bk_username):
    """
        es提取部署参数方法
        @param post_data: 前端post传入的参数信息 参数类型：dict
        @param bk_username: 前端传入的用户名称 参数类型：str
    """
    master_list, data_list, cold_list, client_list = [], [], [], []
    cluster_name = post_data.get('cluster_name')
    app_id = post_data.get('app_id')
    app = post_data.get('app')
    http_port = post_data.get('http_port')
    version = post_data.get('version')
    master_list = str_trans_list(post_data.get('master_list'))
    data_list = str_trans_list(post_data.get('data_list'))
    # spec,集群模式：mixed,dedicated
    spec = post_data.get('spec')
    if len(post_data.get('client_list')) != 0:
        client_list = str_trans_list(post_data.get('client_list'))

    if len(post_data.get('cold_list')) != 0:
        cold_list = str_trans_list(post_data.get('cold_list'))

    description = post_data.get('description')
    account = post_data.get('account')
    password = post_data.get('password')
    master_str = ",".join(master_list)

    if EsCluster.objects.filter(cluster_name=cluster_name).exists():
        return build_fail_result(f"集群名称已存在：{cluster_name}")

    if spec == 'dedicated' and len(master_list) < 3:
        return build_fail_result(f"master节点数量少于3，不满足平台部署最小集群标准。目前节点数量：{len(master_list)}")

    if spec == 'dedicated' and len(data_list) < 2:
        return build_fail_result(f"data节点数量少于2，不满足平台部署最小集群标准。目前节点数量：{len(data_list)}")

    all_ips = master_list + data_list + cold_list + client_list
    if len(all_ips) != len(set(all_ips)):
        return build_fail_result("待部署集群存在重复节点，请检测输入")

    check_result = check_es_add_ip(bk_username, all_ips, app_id, app)
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
            "http_port": http_port,
            "master_list": master_list,
            "data_list": data_list,
            "cold_list": cold_list,
            "client_list": client_list,
            "master_str": master_str,
            "account": account,
            "password": password,
            "description": description,
            "bk_username": bk_username,
            "task_type": 3,
            "spec": spec,
        }
    }


def retrieval_es_add_node_param(post_data, bk_username):
    """
       提取es node节点扩容参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """

    add_ips = str_trans_list(post_data.get('ips'))
    cluster_name = post_data.get('cluster_name')
    role = post_data.get('role')

    cluster = EsCluster.objects.get(cluster_name=cluster_name)
    cluster_id = cluster.id
    version = cluster.version
    master_str = cluster.master_list
    http_port = cluster.http_port
    app_id = cluster.app_id
    app = cluster.app

    check_result = check_es_add_ip(bk_username, add_ips, app_id, app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    return {
        "code": 1,
        "data": {
            "app_id": int(app_id),
            "app": app,
            "cluster_name": cluster_name,
            "cluster_id": cluster_id,
            "version": version,
            "http_port": http_port,
            f"{role}_list": add_ips,
            "role": role,
            "master_str": master_str,
            "bk_username": bk_username,
            "task_type": 10
        }
    }


def retrieval_es_reduce_node_param(post_data, bk_username):
    """
       提取es node节点缩容参数方法(只支持data node 的缩容)
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    reduce_ips = str_trans_list(post_data.get('ips'))
    cluster_name = post_data.get('cluster_name')
    cluster = EsCluster.objects.get(cluster_name=cluster_name)
    cluster_id = cluster.id
    version = cluster.version
    master_str = cluster.master_list
    http_port = cluster.http_port
    app_id = cluster.app_id
    app = cluster.app

    check_result = check_es_add_ip(bk_username, reduce_ips, app_id, app)
    if not check_result:
        # 检测结果不为空，证明检测不通过
        return check_result
    return {
        "code": 1,
        "data": {
            "app_id": int(app_id),
            "cluster_name": cluster_name,
            "cluster_id": cluster_id,
            "version": version,
            "http_port": http_port,
            "target_ips": reduce_ips,
            "master_str": master_str,
            "bk_username": bk_username,
            "task_type": 11
        }
    }


def retrieval_es_input_param(post_data, bk_username):
    """
       提取es 集群录入参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    app_id = post_data.get('app_id')
    app = post_data.get('app')
    cluster_name = post_data.get('cluster_name')
    version = post_data.get('version')
    input_http_url = post_data.get('input_http_url').strip()
    account = post_data.get('account')
    password = post_data.get('password')
    description = post_data.get('description')
    target_ip = input_http_url.split(":")[0]

    if EsCluster.objects.filter(cluster_name=cluster_name).exists():
        return build_fail_result(f"集群名称已存在：{cluster_name}")

    check_result = check_es_add_ip(bk_username, [target_ip], app_id, app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    return {
        "code": 1,
        "data": {
            "app_id": int(app_id),
            "app": app,
            "cluster_name": cluster_name,
            "version": version,
            "input_http_url": input_http_url,
            "account": account,
            "password": password,
            "description": description,
            "target_ip": target_ip,
            "bk_username": bk_username,
            "is_read_success_message": True,
            "task_type": 9
        }
    }
