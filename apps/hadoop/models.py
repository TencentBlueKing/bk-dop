# -*- coding:utf-8 _*-
from django.db import models, transaction

from blueapps.utils.logger import logger
from common.utils.common import get_host_str
from common.utils.constant import hadoop_package_full_name_dict


'''
@summary: 定义hadoop后台管理数据表
@usage:
'''


class ClusterInfo(models.Model):
    """
    定义hadoop集群信息表，记录每一条在线集群的信息情况。
    """

    CLUSTER_STATUS = (
        (0, "已下线"),
        (1, "部署中"),
        (2, "部署异常"),
        (3, "上线中"),
        (4, "集群变更中"),
        (5, "集群异常"),
        (6, "集群录入中"),
        (7, "集群录入异常"),
        (8, "集群回收中"),
        (99, "未知状态"),
    )
    ADD_TYPE = ((0, "平台录入"), (1, "平台新建"))
    cluster_id = models.BigAutoField(primary_key=True, verbose_name="自增列集群id")
    app = models.CharField(max_length=100, default='', verbose_name="业务")
    app_id = models.IntegerField(default=0, verbose_name="业务ID")
    add_type = models.IntegerField(choices=ADD_TYPE, default=1, verbose_name="集群创建方式")
    cluster_status = models.IntegerField(choices=CLUSTER_STATUS, default=99, verbose_name="集群状态")
    cluster_name = models.CharField(max_length=50, unique=True, verbose_name="集群名称")
    cluster_version = models.CharField(max_length=10, verbose_name="集群版本")
    cluster_user = models.CharField(max_length=16, default="hadoop", verbose_name="集群启动用户")
    base_dir = models.CharField(max_length=128, default="/data/hadoop_env", verbose_name="集群安装目录")
    hdfs_includes = models.CharField(
        max_length=128, default="/data/hadoop_env/hadoop/etc/hadoop/includes", verbose_name="集群hdfs白名单路径"
    )
    hdfs_excludes = models.CharField(
        max_length=128, default="/data/hadoop_env/hadoop/etc/hadoop/excludes", verbose_name="集群hdfs黑名单路径"
    )
    hdfs_data_dir = models.CharField(max_length=128, verbose_name="datanode数据目录")
    hdfs_repl_num = models.IntegerField(default=2, verbose_name="hdfs文件副本数")
    ssh_port = models.IntegerField(default=22, verbose_name="ssh远程端口号")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="集群创建时间")
    create_user = models.CharField(max_length=256, default="system", verbose_name="集群创建者")
    zk_port = models.IntegerField(default=2181, verbose_name="zookeeper访问端口")
    metric_port = models.IntegerField('监控exporter插件对应的访问端口', default=29999)
    bk_data_id = models.IntegerField('监控平台对应DATA ID,0代表尚未部署监控', default=0)
    access_token = models.CharField("监控平台对应查询的token,用于查询监控数据", max_length=128, default="null")
    bk_group_id = models.IntegerField('监控平台对应group_id ,0代表尚未部署监控', default=0)

    class Meta:
        db_table = "t_hadoop_cluster_info"
        verbose_name = "Hadoop集群信息表"
        verbose_name_plural = "Hadoop集群信息表"


class ClusterDetail(models.Model):

    """
    定义hadoop集群生态信息，定义每类组件的每个进程信息，与集群信息表一对多对应
    """

    PROCESS_STATUS = ((0, "已运行"), (1, "已关闭"), (2, "待回收"), (99, "未知状态"))

    app_id = models.IntegerField('业务id', default=0)
    process_id = models.BigAutoField(primary_key=True, verbose_name="自增列进程id")
    cluster_id = models.IntegerField(default=0, verbose_name="关联的集群ID")
    process_name = models.CharField(max_length=15, verbose_name="进程名称")
    hadoop_group_name = models.CharField(max_length=15, verbose_name="hadoop生态组件")
    process_ip = models.CharField(max_length=15, verbose_name="进程所在ip")
    process_hostname = models.CharField(max_length=128, verbose_name="进程所在hostname")
    process_status = models.IntegerField(choices=PROCESS_STATUS, default=99, verbose_name="进程状态")
    package_version = models.CharField(max_length=10, verbose_name="进程版本")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="进程加入时间")

    class Meta:
        db_table = "t_hadoop_cluster_detail"
        verbose_name = "Hadoop集群进程信息"
        verbose_name_plural = "Hadoop集群进程信息"
        unique_together = ('process_name', 'process_ip')


def create_cluster_info(init_info):
    """
      部署hadoop集群初始化数据库信息
      "init_info": {
            "app_id": int(app_id),
            "hosts_info": hosts_info,
            "cluster_name": cluster_name,
            "cluster_user": cluster_user,
            "base_dir": base_dir,
            "hdfs_includes": hdfs_includes,
            "hdfs_excludes": hdfs_excludes,
            "cluster_version": cluster_version,
            "clean_data_force": clean_data_force,
            "ssh_port": int(ssh_port),
            "namenode": namenode_list,
            "datanode": datanode_list,
            "standbynamenode": standby_namenode_list,
            "resourcemanager": resourcemanager_list,
            "nodemanager": nodemanager_list,
            "zookeepernode": zookeepernode_list,
            "journalnode": journalnode_list,
            "data_disk_dir_list": data_disk_dir_list,
            "replication_number": int(replication_number),
            "task_type": task_type,
            "ops_type": ops_type
            }
    """

    try:
        with transaction.atomic():
            # insert t_hadoop_cluster_info
            cluster = ClusterInfo.objects.create(
                app_id=init_info['app_id'],
                app=init_info['app'],
                cluster_status=3,
                add_type=init_info['add_type'],
                cluster_name=init_info['cluster_name'],
                cluster_version=init_info['cluster_version'],
                cluster_user=init_info['cluster_user'],
                base_dir=init_info['base_dir'],
                hdfs_includes=init_info['hdfs_includes'],
                hdfs_excludes=init_info['hdfs_excludes'],
                hdfs_data_dir=",".join(init_info['data_disk_dir_list']),
                hdfs_repl_num=init_info['replication_number'],
                ssh_port=init_info['ssh_port'],
                create_user=init_info['bk_username'],
                zk_port=init_info['zk_port'],
            )
            # 获取插入后的cluster_id
            for namenode_ip in init_info['namenode']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="NameNode",
                    hadoop_group_name="hdfs",
                    process_ip=namenode_ip,
                    process_status=0,
                    process_hostname=get_host_str([namenode_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['hadoop']['version'],
                )

            for standbynamenode_ip in init_info['standbynamenode']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="StandbyNameNode",
                    hadoop_group_name="hdfs",
                    process_ip=standbynamenode_ip,
                    process_status=0,
                    process_hostname=get_host_str([standbynamenode_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['hadoop']['version'],
                )

            for datanode_ip in init_info['datanode']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="DataNode",
                    hadoop_group_name="hdfs",
                    process_ip=datanode_ip,
                    process_status=0,
                    process_hostname=get_host_str([datanode_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['hadoop']['version'],
                )
            for journalnode_ip in init_info['journalnode']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="JournalNode",
                    hadoop_group_name="hdfs",
                    process_ip=journalnode_ip,
                    process_status=0,
                    process_hostname=get_host_str([journalnode_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['hadoop']['version'],
                )

            for zookeepernode_ip in init_info['zookeepernode']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="Zookeeper",
                    hadoop_group_name="zookeeper",
                    process_ip=zookeepernode_ip,
                    process_status=0,
                    process_hostname=get_host_str([zookeepernode_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['zookeeper']['version'],
                )

            for resourcemanager_ip in init_info['resourcemanager']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="ResourceManager",
                    hadoop_group_name="yarn",
                    process_ip=resourcemanager_ip,
                    process_status=0,
                    process_hostname=get_host_str([resourcemanager_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['hadoop']['version'],
                )

            for nodemanager_ip in init_info['nodemanager']:
                ClusterDetail.objects.create(
                    app_id=init_info['app_id'],
                    cluster_id=cluster.cluster_id,
                    process_name="NodeManager",
                    hadoop_group_name="yarn",
                    process_ip=nodemanager_ip,
                    process_status=0,
                    process_hostname=get_host_str([nodemanager_ip], init_info['hosts_info']),
                    package_version=hadoop_package_full_name_dict[init_info['cluster_version']]['hadoop']['version'],
                )
    except Exception as err:
        logger.error(str(err))
        return None

    return cluster.cluster_id


def insert_cluster_detail_info(update_info):
    """
       扩容后插入新的进程信息
    """
    insert_process_id_list = []
    try:
        with transaction.atomic():
            for host in update_info['hosts_info']:
                if host['process_add'] == 1:

                    process_info = ClusterDetail.objects.create(
                        app_id=update_info['app_id'],
                        cluster_id=update_info['cluster_id'],
                        process_name=update_info['process_name'],
                        hadoop_group_name=update_info['hadoop_group_name'],
                        process_ip=host['ip'],
                        process_status=0,
                        process_hostname=get_host_str([host['ip']], update_info['hosts_info']),
                        package_version=update_info['cluster_version'],
                    )
                    insert_process_id_list.append(process_info.process_id)
    except Exception as err:
        logger.error(str(err))

    return insert_process_id_list


def delete_cluster_detail_info(process_id_list):
    """
       缩容后删除的进程信息
    """
    try:
        with transaction.atomic():
            for delete_process_id in process_id_list:
                ClusterDetail.objects.filter(process_id=delete_process_id).delete()
            return True

    except Exception as err:
        logger.error(f"hadoop集群数据删除缩容节点信息发生异常{str(err)}")
        return False


def update_cluster_status(cluster_id, update_data):
    """
       更新cluster的数据
       参数：cluster_id: 集群id update_data:更新数据
    """
    try:
        ClusterInfo.objects.filter(cluster_id=cluster_id).update(**update_data)
        return True

    except Exception as err:
        logger.error(str(err))
        return False


def delete_cluster_info(cluster_id):
    """
       删除数据库关于集群所有信息
       参数：process_id: 进程id cluster_id: 集群id process_status: 进程状态
    """
    try:
        # 如果cluster_id 不为空，则代表安装cluster_id 来更新状态
        with transaction.atomic():
            ClusterInfo.objects.filter(cluster_id=cluster_id).delete()
            ClusterDetail.objects.filter(cluster_id=cluster_id).delete()
        return True

    except Exception as err:
        logger.error(f"hadoop集群数据删除发生异常{str(err)}")
        return False


def update_process_status(update_data, process_id_list=None, cluster_id=None):
    """
       更新cluster集群内部节点的属性信息
       参数：process_id: 进程id cluster_id: 集群id update_data: 更新数据格式dict，记录需要更新的数据
    """
    try:
        # 如果cluster_id 不为空，则代表安装cluster_id 来更新状态
        if cluster_id:
            ClusterDetail.objects.filter(cluster_id=cluster_id).update(**update_data)
        else:
            ClusterDetail.objects.filter(process_id__in=process_id_list).update(**update_data)
        return True

    except Exception as err:
        logger.error(str(err))
        return False


def get_datanode_info(cluster_id):
    datanode_list = []
    try:
        datanode_infos = ClusterDetail.objects.filter(
            cluster_id=cluster_id, process_name="DataNode", process_status=0
        ).values('process_id', 'process_ip')
        for datanode_info in datanode_infos:
            datanode_list.append({"process_id": datanode_info['process_id'], "process_ip": datanode_info['process_ip']})
        return datanode_list

    except Exception as err:
        logger.error(str(err))
        return None
