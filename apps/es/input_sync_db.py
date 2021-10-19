# -*- coding:utf-8 _*-
import json

from apps.es.models import EsCluster, EsNodeInfo
from common.utils.common import get_cc_info_by_ip


'''
@summary: 集群录入后同步数据库
@usage:
'''


def sync_db(node_info, input_info):
    """
       获取成功后录入db信息
       @param node_info: 执行成功后返回集群json信息 参数类型：str/dict
       @param input_info: 执行集群录入任务的任务参数 参数类型：dict
    """
    if not isinstance(node_info, dict):
        node_info = json.loads(node_info)

    master_node_sum = 0
    data_node_sum = 0
    cold_node_sum = 0
    client_node_sum = 0
    master_list = []
    http_port = input_info['input_http_url'].split(':')[1]

    for node in node_info:
        node_name = node.get('name')
        ip = node.get('ip')
        role_list = []
        if node.get('node.role') == 'ir' or node.get('node.role') == 'r' or node.get('node.role') == '':
            role_list.append("client")
            client_node_sum += 1
        if node.get('node.role').find('c') != -1:
            role_list.append("cold")
            cold_node_sum += 1
        if node.get('node.role').find('d') != -1:
            role_list.append("data")
            data_node_sum += 1
        if node.get('node.role').find('m') != -1:
            role_list.append("master")
            master_list.append(ip)
            master_node_sum += 1

        # 尝试获取机器的硬件信息
        res = get_cc_info_by_ip(input_info['bk_username'], input_info['app_id'], ip)
        device_class = res['data']['info'][0].get('svr_device_class', 'Not Available')
        hard_memo = res['data']['info'][0].get('hard_memo', 'Not Available')

        EsNodeInfo.objects.create(
            app_id=int(input_info['app_id']),
            cluster_name=input_info['cluster_name'],
            node_name=node_name,
            role=",".join(role_list),
            ip=ip,
            version=input_info['version'],
            device_class=device_class,
            hard_memo=hard_memo,
        )

    cluster = EsCluster.objects.create(
        cluster_name=input_info['cluster_name'],
        app=input_info['app'],
        app_id=int(input_info['app_id']),
        master_list=",".join(master_list),
        master_cnt=master_node_sum,
        data_cnt=data_node_sum,
        cold_cnt=cold_node_sum,
        client_cnt=client_node_sum,
        version=input_info['version'],
        http_port=http_port,
        description=input_info['description'],
        created_by=input_info['bk_username'],
        add_type=0,
    )
    return cluster.id
