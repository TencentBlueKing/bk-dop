# -*- coding:utf-8 _*-

from apps.hadoop.models import ClusterDetail, ClusterInfo
from common.utils.common import (
    build_fail_result,
    create_host_name,
    find_host_name,
    get_cc_info_by_ip,
    is_dir,
    is_ip,
    str_trans_list,
)
from common.utils.monitor_sdk import MonitorExecutor

'''
@summary: 定义不同Hadoop任务参数处理模块：参数检测，参数提取
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


def check_hadoop_add_ip(bk_username, ip_list, app_id, app):
    """
       提取公共检测ip的代码来封装，减少重复代码
       @param bk_username: ip在配置平台检测需要的用户名称 参数类型： str
       @param ip_list: 任务中新加的带检测ip列表，参数类型: list/set
       @param app_id: ip在配置平台检测需要的业务ID 参数类型： int
       @param app: ip的配置平台检测需要的业务名称 参数类型： str
    """
    for node_ip in ip_list:
        if not is_ip(node_ip):
            # 存在非法ip
            return build_fail_result(f"存在非法IP:{node_ip}")
        if ClusterDetail.objects.filter(process_ip=node_ip).exists():
            # ip已录入平台
            return build_fail_result(f"平台检测到存在该IP:{node_ip}")

        if get_cc_info_by_ip(bk_username=bk_username, app_id=app_id, ip=node_ip)['data']['count'] == 0:
            # 节点不属于对应业务，异常退出

            return build_fail_result(f"节点不属于对应业务{app}，请自查:{node_ip}")

    return None


def retrieval_hadoop_deploy_param(post_data, bk_username):
    """
       针对hadoop集群部署或者录入做传入做参数检测，若检测失败则返回异常
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """

    # global config

    app_id = post_data.get("app_id")
    app = post_data.get('app')
    add_type = post_data.get("add_type")
    cluster_name = post_data.get("cluster_name")
    cluster_version = post_data.get("cluster_version")
    cluster_user = post_data.get("cluster_user")
    base_dir = post_data.get("base_dir")
    hdfs_includes = post_data.get("hdfs_includes") if post_data.get("hdfs_includes") != '' else "no config file"
    hdfs_excludes = post_data.get("hdfs_excludes") if post_data.get("hdfs_excludes") != '' else "no config file"
    data_disk_dir_list = str_trans_list(post_data.get("hdfs_dir"))
    replication_number = post_data.get("repl_number")
    ssh_port = post_data.get("ssh_port")
    is_create_bk_monitor = int(post_data.get('is_create_bk_monitor'))

    # zk
    zk_port = post_data.get('zookeeperport', '2181') if post_data.get("zookeeperport") != '' else "0"
    zookeepernode_list = str_trans_list(post_data.get("zookeepernode", ""))

    # hdfs
    namenode_list = str_trans_list(post_data.get("namenode", ""))
    standby_namenode_list = str_trans_list(post_data.get("standbynamenode", ""))
    datanode_list = str_trans_list(post_data.get("datanode", ""))
    journalnode_list = str_trans_list(post_data.get("journalnode", ""))

    # yarn
    resourcemanager_list = str_trans_list(post_data.get("resourcemanagernode", ""))
    nodemanager_list = str_trans_list(post_data.get("nodemanagernode", ""))

    # 录入功能专属参数，域名映射信息
    hostname_to_ip_list = str_trans_list(post_data.get("hostname_list", ""))

    # 1.1:检测输入的每个数据目录是否合法
    for dir_str in data_disk_dir_list:
        if not is_dir(dir_str):
            return build_fail_result("数据目录存在不合法目录，请仔细配置")

    if add_type == 1 and (hdfs_excludes == hdfs_includes):
        return build_fail_result("白名单配置和黑名单配置一致，请仔细配置")

    # 1.2:检测传入的cluster_name是否报错，如果存在则返回异常
    hadoop_cluster_info = ClusterInfo.objects.filter(cluster_name=cluster_name).exists()
    if hadoop_cluster_info:
        return build_fail_result("cluster_name名称已存在")

    # 1.3:检测集群配置是否存在异常

    ip_list = set(
        namenode_list
        + standby_namenode_list
        + journalnode_list
        + zookeepernode_list
        + datanode_list
        + resourcemanager_list
        + nodemanager_list
    )

    # 1.4:检验ip_list
    # 和相关的组件的ip数量是否标准：比如namenode需要2个节点，journalnode需要3节点，zk需要3节点等等
    if add_type == 1 and (0 <= len(ip_list) < 3):
        # 集群节点必须大于等于3
        return build_fail_result("整体集群节点必须小于3")

    check_result = check_hadoop_add_ip(bk_username, ip_list, app_id, app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    if add_type == 0 and len(namenode_list) != 1:
        # 录入集群时nn节点数量不等于1
        return build_fail_result("NameNode节点有且仅有1个，请检测录入信息")

    if add_type == 1 and (len(namenode_list) != 1 or
                          len(standby_namenode_list) != 1 or
                          namenode_list == standby_namenode_list):
        # NameNode节点和standby_NameNode节点有且仅有1个，而且不能同等
        return build_fail_result("NameNode节点和standby_NameNode节点有且仅有1个，而且不能同等")

    if add_type == 1 and len(journalnode_list) < 3:
        # JournalNode节点数量小于3
        return build_fail_result("JournalNode节点数量要等于大于3")

    if add_type == 1 and len(zookeepernode_list) < 3:
        # ZookeeperNode节点数量小于3
        return build_fail_result("ZookeeperNode节点数量要等于大于3")

    if len(datanode_list) < int(replication_number):
        # datanode 节点少于副本数
        return build_fail_result("datanode节点数量必须大于等于hdfs副本数量")

    if resourcemanager_list and (len(resourcemanager_list) != 2 or not nodemanager_list):
        # ResourceManager存在，且节点不等于2,或者NodeManager数量不等于0情况
        return build_fail_result("ResourceManager存在，但检测到节点数量不等于2,或者NodeManager配置为空")

    # 1.5:根据add_type的值和resourcemanager_list 是否为空，判断是什么录入/部署类型
    if int(add_type) == 0:
        task_type = 9
        ops_type = "other"
    elif len(resourcemanager_list) == 0:
        task_type = 3
        ops_type = "only_hdfs"
    else:
        task_type = 3
        ops_type = "hdfs_yarn"

    # 1.5:按照规则生成每个机器的deploy的元信息，包括hostname，需要启动那些进程等，形成host_info列表存入参数
    hosts_info = []
    for ip in ip_list:
        host_name = (
            create_host_name(cluster_name, ip) if int(add_type) == 1 else find_host_name(hostname_to_ip_list, ip)
        )
        if not host_name:
            return build_fail_result("该ip({})无法找到对应的域名信息记录，请检测域名映射表的信息记录".format(ip))
        info = {"ip": ip, "user": "hadoop", "add": 1, "process_add": 1, "host_name": host_name}
        hosts_info.append(info)

    return {
        "code": 1,
        "data": {
            "app_id": int(app_id),
            "app": app,
            "add_type": int(add_type),
            "hosts_info": hosts_info,
            "cluster_name": cluster_name,
            "cluster_user": cluster_user,
            "base_dir": base_dir,
            "hdfs_includes": hdfs_includes,
            "hdfs_excludes": hdfs_excludes,
            "cluster_version": cluster_version,
            "ssh_port": int(ssh_port),
            "namenode": namenode_list,
            "datanode": datanode_list,
            "standbynamenode": standby_namenode_list,
            "resourcemanager": resourcemanager_list,
            "nodemanager": nodemanager_list,
            "zk_port": int(zk_port),
            "zookeepernode": zookeepernode_list,
            "journalnode": journalnode_list,
            "data_disk_dir_list": data_disk_dir_list,
            "replication_number": int(replication_number),
            "task_type": task_type,
            "ops_type": ops_type,
            "bk_username": bk_username,
            "hostname_list": hostname_to_ip_list,
            "is_create_bk_monitor": is_create_bk_monitor
        },
    }


def retrieval_hadoop_add_node_param(post_data, bk_username):
    """
       提取hadoop datanode节点扩容参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_id = post_data.get('cluster_id')
    scaled_up_ip_list = str_trans_list(post_data.get("ips", ""))
    cluster_info = ClusterInfo.objects.get(cluster_id=cluster_id)

    # 检测 cluster_id 是否异常
    if not cluster_info:
        return build_fail_result("集群信息在后台数据不存在:{}".format(cluster_id))
    if cluster_info.cluster_status != 3:
        return build_fail_result("集群在非运行中状态下，不能发起集群变更任务，请检测集群当前状态")

    # 判断是什么节点扩容类型

    ops_type = "only_hdfs"
    process_name = "DataNode"
    hadoop_group_name = "hdfs"

    # 检测待扩容机器的是否适合扩容标准
    if not scaled_up_ip_list:
        return build_fail_result("待添加IP列表为空")

    for add_ip in scaled_up_ip_list:
        if not is_ip(add_ip):
            return build_fail_result("检测到非法ip信息:{}".format(add_ip))

        if ClusterDetail.objects.filter(process_ip=add_ip, process_name=process_name).exists():
            return build_fail_result("该节点已经部署对应的进程信息:{}_{}".format(add_ip, process_name))

        process_infos = ClusterDetail.objects.filter(process_ip=add_ip).values()
        if process_infos:
            for process_info in process_infos:
                if process_info['process_name'] == process_name:
                    return build_fail_result("该节点已经部署对应的进程信息:{}_{}".format(add_ip, process_name))

                if process_info['cluster_id'] != cluster_id:
                    return build_fail_result(
                        "检测到待扩容机器已经部署其他集群:报错机器ip:{},ip所有集群id:{}".format(add_ip, process_info['cluster_id'])
                    )

    # 生成整体的集群信息
    hosts_info = []
    name_node_list = []
    standby_name_node_list = []
    data_node_list = []
    zookeeper_node_list = []
    journal_node_list = []
    resource_manager_list = []
    node_manager_list = []
    exist_ip_list = []
    add_host_info_ip_list = []
    cluster_detail = ClusterDetail.objects.filter(cluster_id=cluster_id).values()
    for process_info in cluster_detail:

        process_add = 0
        if process_info['process_ip'] in scaled_up_ip_list and process_info['process_ip'] not in exist_ip_list:
            exist_ip_list.append(process_info['process_ip'])
            process_add = 1

        if process_info['process_ip'] not in add_host_info_ip_list:
            hosts_info.append(
                {
                    "ip": process_info['process_ip'],
                    "user": "hadoop",
                    "add": 0,
                    "process_add": process_add,
                    "host_name": process_info['process_hostname'],
                }
            )
            add_host_info_ip_list.append(process_info['process_ip'])

        if process_info['process_name'] == 'NameNode':
            name_node_list.append(process_info['process_ip'])
            continue
        elif process_info['process_name'] == 'StandbyNameNode':
            standby_name_node_list.append(process_info['process_ip'])
            continue
        elif process_info['process_name'] == 'DataNode':
            data_node_list.append(process_info['process_ip'])
            continue
        elif process_info['process_name'] == 'JournalNode':
            journal_node_list.append(process_info['process_ip'])
            continue
        elif process_info['process_name'] == 'Zookeeper':
            zookeeper_node_list.append(process_info['process_ip'])
            continue
        elif process_info['process_name'] == 'ResourceManager':
            resource_manager_list.append(process_info['process_ip'])
            continue
        elif process_info['process_name'] == 'NodeManager':
            node_manager_list.append(process_info['process_ip'])
            continue

    # 获取集群基本信息
    add_ips = set(scaled_up_ip_list) - set(exist_ip_list)

    # 检测新加的机器是否符合部署规则
    check_result = check_hadoop_add_ip(bk_username, add_ips, cluster_info.app_id, cluster_info.app)
    if check_result:
        # 检测结果不为空，证明检测不通过
        return check_result

    for add_ip in add_ips:
        hosts_info.append(
            {
                "ip": add_ip,
                "user": "hadoop",
                "add": 1,
                "process_add": 1,
                "host_name": create_host_name(cluster_info.cluster_name, add_ip),
            }
        )

    return {
        "code": 1,
        "data": {
            "app_id": cluster_info.app_id,
            "hosts_info": hosts_info,
            "cluster_name": cluster_info.cluster_name,
            "cluster_id": int(cluster_info.cluster_id),
            "cluster_version": cluster_info.cluster_version,
            "cluster_user": cluster_info.cluster_user,
            "base_dir": cluster_info.base_dir,
            "hdfs_includes": cluster_info.hdfs_includes,
            "hdfs_excludes": cluster_info.hdfs_excludes,
            "ssh_port": int(cluster_info.ssh_port),
            "namenode": name_node_list,
            "datanode": data_node_list,
            "standbynamenode": standby_name_node_list,
            "resourcemanager": resource_manager_list,
            "nodemanager": node_manager_list,
            "zookeepernode": zookeeper_node_list,
            "journalnode": journal_node_list,
            "data_disk_dir_list": str(cluster_info.hdfs_data_dir).split(','),
            "replication_number": int(cluster_info.hdfs_repl_num),
            "task_type": 4,
            "ops_type": ops_type,
            "process_name": process_name,
            "hadoop_group_name": hadoop_group_name,
            "bk_username": bk_username,
            "scaled_up_ip_list": scaled_up_ip_list,
        },
    }


def retrieval_hadoop_add_dir_param(post_data, bk_username):
    """
       提取hadoop 目录扩容参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_id = post_data.get('cluster_id')
    scaled_up_dir_list = str_trans_list(post_data.get("data_dir", ""))
    cluster_info = ClusterInfo.objects.get(cluster_id=cluster_id)

    # 检测 cluster_id 是否异常
    if not cluster_info:
        return build_fail_result(f"集群信息在后台数据不存在:{cluster_id}")
    if cluster_info.cluster_status != 3:
        return build_fail_result("集群在非运行中状态下，不能发起集群变更任务，请检测集群当前状态")

    # 检测待添加目录配置是否正常
    if not scaled_up_dir_list:
        return build_fail_result("待添加目录列表为空")

    for add_dir in scaled_up_dir_list:
        if not is_dir(add_dir):
            return build_fail_result(f"检测到非法目录配置:{add_dir}")

        if str(cluster_info.hdfs_data_dir).find(add_dir) != -1:
            return build_fail_result(f"待扩容磁盘已存在部署,请检测:{add_dir}")

    # 生成整体集群信息
    hosts_info = []
    data_node_list = []
    add_hosts_info_ip_list = []

    cluster_detail = ClusterDetail.objects.filter(cluster_id=cluster_id).values()
    for process_info in cluster_detail:
        if process_info['process_ip'] not in add_hosts_info_ip_list:
            hosts_info.append(
                {
                    "ip": process_info['process_ip'],
                    "user": "hadoop",
                    "add": 0,
                    "process_add": 0,
                    "host_name": process_info['process_hostname'],
                }
            )
            add_hosts_info_ip_list.append(process_info['process_ip'])

        if process_info['process_name'] == 'DataNode':
            data_node_list.append(process_info['process_ip'])

    return {
        "code": 1,
        "data": {
            "app_id": cluster_info.app_id,
            "hosts_info": hosts_info,
            "datanode": data_node_list,
            "cluster_name": cluster_info.cluster_name,
            "cluster_user": cluster_info.cluster_user,
            "base_dir": cluster_info.base_dir,
            "cluster_id": cluster_info.cluster_id,
            "old_dir_str": cluster_info.hdfs_data_dir,
            "scaled_up_dir_list": scaled_up_dir_list,
            "task_type": 8,
            "bk_username": bk_username,
        },
    }


def retrieval_hadoop_remove_node_param(post_data, bk_username):
    """
       提取hadoop 节点缩容参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_id = post_data.get('cluster_id')
    process_id_list = post_data.get("process_id_list", [])
    cluster_info = ClusterInfo.objects.get(cluster_id=cluster_id)

    # 检测 cluster 是否异常
    if not cluster_info:
        return build_fail_result(f"集群信息在后台数据不存在:{cluster_id}")
    if cluster_info.cluster_status != 3:
        return build_fail_result("集群在非运行中状态下，不能发起集群变更任务，请检测集群当前状态")

    for process_id in process_id_list:
        if not ClusterDetail.objects.filter(process_id=process_id).exists():
            return build_fail_result("检测到待回收的进程信息不存在:{}".format(process_id))

    data_num = ClusterDetail.objects.filter(cluster_id=cluster_id, process_name="DataNode").count()
    if int(data_num) - len(process_id_list) < int(cluster_info.hdfs_repl_num):
        return build_fail_result("剩余datanode数量少于副本数量，不允许回收")

    # 生成整体集群信息
    hosts_info = []
    add_hosts_info_ip_list = []
    recycle_ip_list = []
    for ip_list in ClusterDetail.objects.filter(process_id__in=process_id_list).values('process_ip'):
        recycle_ip_list.append(ip_list['process_ip'])

    cluster_detail = ClusterDetail.objects.filter(cluster_id=cluster_id).values()
    for process_info in cluster_detail:

        if process_info['process_ip'] not in add_hosts_info_ip_list:
            hosts_info.append(
                {
                    "ip": process_info['process_ip'],
                    "user": "hadoop",
                    "add": 0,
                    "process_add": -1 if process_info['process_ip'] in recycle_ip_list else 0,
                    "host_name": process_info['process_hostname'],
                }
            )
            add_hosts_info_ip_list.append(process_info['process_ip'])

    return {
        "code": 1,
        "data": {
            "app_id": cluster_info.app_id,
            "hosts_info": hosts_info,
            "cluster_name": cluster_info.cluster_name,
            "cluster_user": cluster_info.cluster_user,
            "base_dir": cluster_info.base_dir,
            "hdfs_includes": cluster_info.hdfs_includes,
            "hdfs_excludes": cluster_info.hdfs_excludes,
            "cluster_id": cluster_id,
            "datanode": recycle_ip_list,
            "task_type": 5,
            "process_id_list": process_id_list,
            "bk_username": bk_username,
        },
    }


def retrieval_hadoop_install_monitor_param(post_data, bk_username):
    """
       提取hadoop 添加监控参数方法
       @param post_data: 前端post传入的参数信息 参数类型：dict
       @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_name = post_data.get('cluster_name')
    cluster = ClusterInfo.objects.get(cluster_name=cluster_name)
    cluster_id = cluster.cluster_id
    app_id = cluster.app_id
    version = cluster.cluster_version
    hadoop_ips = ClusterDetail.objects.filter(cluster_id=cluster_id).values('process_ip').distinct()
    target_ips = [info.get('process_ip') for info in hadoop_ips]

    monitor = MonitorExecutor(bk_username)
    bk_data_id, access_token, bk_group_id = monitor.create_monitor_data(app_id, f"hadoop_{cluster_name}")
    # 目前指定hadoop exporter 开放端口为29999
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
            "version": version,
            "db_type": 2,
            "bk_username": bk_username,
            "task_type": 12
        },
    }


def retrieval_hadoop_destroy_param(post_data, bk_username):
    """
        提取hadoop回收参数方法
        @param post_data: 前端post传入的参数信息 参数类型：dict
        @param bk_username: 前端传入的用户名称 参数类型：str
    """
    cluster_id = int(post_data.get('cluster_id'))
    cluster = ClusterInfo.objects.get(cluster_id=cluster_id)
    hadoop_ips = ClusterDetail.objects.filter(cluster_id=cluster_id).values('process_ip').distinct()
    target_ips = [info.get('process_ip') for info in hadoop_ips]
    cluster_name = cluster.cluster_name
    bk_group_id = cluster.bk_group_id
    app_id = cluster.app_id
    monitor = MonitorExecutor(bk_username)
    if not monitor.delete_monitor_data(app_id, bk_group_id):
        return build_fail_result("删除集群监控配置失败")
    return {
        "code": 1,
        "data": {
            "cluster_id": int(cluster_id),
            "cluster_name": cluster_name,
            "app_id": int(app_id),
            "target_ips": target_ips,
            "bk_username": bk_username,
            "task_type": 13

        }
    }