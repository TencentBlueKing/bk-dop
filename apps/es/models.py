# -*- coding: utf-8 -*-
from django.db import models, transaction
from django.db.models import F

from blueapps.utils.logger import logger
from common.utils.common import get_cc_info_by_ip


class EsNodeInfo(models.Model):
    """
    ES集群节点信息表
    """

    app_id = models.IntegerField('业务id', default=0)
    cluster_name = models.CharField('集群名称', max_length=50, default='', db_index=True)
    node_name = models.CharField('节点名称', max_length=50, default='', db_index=True)
    ip = models.CharField('节点ip', max_length=50, default='')
    role = models.CharField('节点角色', max_length=50, default='')
    version = models.CharField('es版本', max_length=50, default='')
    device_class = models.CharField('设备类型', max_length=50, default='')
    hard_memo = models.CharField('硬件说明', max_length=50, default='')

    class Meta:
        db_table = "t_es_cluster_detail"
        verbose_name = "Es集群节点信息"
        verbose_name_plural = "Es集群节点信息"
        unique_together = ('cluster_name', 'node_name', 'ip')


class EsRule(models.Model):
    """
       ES集群权限信息表
    """
    app = models.CharField('业务', max_length=100, default='')
    app_id = models.IntegerField('业务id', default=0)
    cluster_name = models.CharField('集群名称', max_length=100, default='')
    user_name = models.CharField('用户名称', max_length=100, default='')

    class Meta:
        db_table = "t_es_cluster_role"
        verbose_name = "Es集群用户信息表"
        verbose_name_plural = "Es集群用户信息表"


class EsCluster(models.Model):
    """
        ES集群信息表
    """
    DELETE_STATUS = ((0, '未删除'), (1, '已删除'))
    ADD_TYPE = ((0, "平台录入"), (1, "平台新建"))

    CLUSTER_STATUS = (
        (0, "已下线"),
        (1, "部署中"),
        (2, "部署异常"),
        (3, "上线中"),
        (4, "集群变更中"),
        (5, "集群异常"),
        (6, "集群录入中"),
        (7, "集群录入异常"),
        (99, "未知状态"),
    )

    cluster_name = models.CharField('集群名称', max_length=100, default='', unique=True)
    cluster_status = models.IntegerField(choices=CLUSTER_STATUS, default=3, verbose_name="集群状态")
    app = models.CharField('业务', max_length=100, default='')
    app_id = models.IntegerField('业务id', default=0)
    master_list = models.CharField('master列表', max_length=100, default='')
    master_cnt = models.IntegerField('master数量', default=0)
    data_cnt = models.IntegerField('数据节点数量', default=0)
    cold_cnt = models.IntegerField('冷节点数量', default=0)
    client_cnt = models.IntegerField('协调节点数量', default=0)
    version = models.CharField('版本号', max_length=100, default='')
    http_port = models.CharField('http端口号', max_length=100, default='6300')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True)
    address = models.CharField('版本号', max_length=100, default='')
    description = models.CharField('集群描述', max_length=100, default='')
    created_by = models.CharField('创建人', max_length=256, default='system')
    is_delete = models.IntegerField('删除标志', choices=DELETE_STATUS, default=0)
    add_type = models.IntegerField('集群创建方式', choices=ADD_TYPE, default=1)

    class Meta:
        db_table = "t_es_cluster_info"
        verbose_name = "Es集群信息"
        verbose_name_plural = "Es集群信息"

    def __unicode__(self):
        return '%d: %s' % (self.pk, self.cluster_name)


def insert_es_cluster(deploy_info):
    """
        部署kafka集群初始化数据库信息
        @param deploy_info : {
            "app_id": 业务id,
            "app": 业务名称,
            "add_type": 0/1 添加模式,
            "cluster_name": 集群名称,
            "version": 版本号,
            "http_port": es http 集群端口号,
            "master_list": master节点列表,
            "data_list": data节点列表,
            "cold_list": cold节点列表,
            "client_list": client节点列表,
            "master_str": master节点信息，已逗号隔开,
            "account": 集群初始化账号,
            "password": 集群初始化账号密码,
            "description": 集群描述,
            "bk_username": 创建者,
            "task_type": 任务类型
        }
    """
    try:
        # 绑定事务插入，保证事务的数据一致性
        with transaction.atomic():
            cluster = EsCluster.objects.create(
                cluster_name=deploy_info['cluster_name'],
                app=deploy_info['app'],
                app_id=deploy_info['app_id'],
                master_list=deploy_info['master_str'],
                master_cnt=len(deploy_info['master_list']),
                data_cnt=len(deploy_info['data_list']),
                cold_cnt=len(deploy_info['cold_list']),
                client_cnt=len(deploy_info['client_list']),
                version=deploy_info['version'],
                http_port=deploy_info['http_port'],
                description=deploy_info['description'],
                created_by=deploy_info['bk_username'],
            )
            # 集群信息表插入后，插入node节点信息
            for master_ip in deploy_info['master_list']:
                res = get_cc_info_by_ip(deploy_info['bk_username'], deploy_info['app_id'], master_ip)
                device_class = res['data']['info'][0].get('svr_device_class', 'Not Available')
                hard_memo = res['data']['info'][0].get('hard_memo', 'Not Available')

                EsNodeInfo.objects.create(
                    app_id=deploy_info['app_id'],
                    cluster_name=deploy_info['cluster_name'],
                    node_name=f"master-{master_ip}",
                    role='master',
                    ip=master_ip,
                    version=deploy_info['version'],
                    device_class=device_class,
                    hard_memo=hard_memo,
                )
            for data_ip in deploy_info['data_list']:
                res = get_cc_info_by_ip(deploy_info['bk_username'], deploy_info['app_id'], data_ip)
                device_class = res['data']['info'][0].get('svr_device_class', 'Not Available')
                hard_memo = res['data']['info'][0].get('hard_memo', 'Not Available')

                EsNodeInfo.objects.create(
                    app_id=deploy_info['app_id'],
                    cluster_name=deploy_info['cluster_name'],
                    node_name=f"dn-{data_ip}",
                    role='data',
                    ip=data_ip,
                    version=deploy_info['version'],
                    device_class=device_class,
                    hard_memo=hard_memo,
                )
            for cold_ip in deploy_info['cold_list']:
                res = get_cc_info_by_ip(deploy_info['bk_username'], deploy_info['app_id'], cold_ip)
                device_class = res['data']['info'][0].get('svr_device_class', 'Not Available')
                hard_memo = res['data']['info'][0].get('hard_memo', 'Not Available')

                EsNodeInfo.objects.create(
                    app_id=deploy_info['app_id'],
                    cluster_name=deploy_info['cluster_name'],
                    node_name=f"cold-{cold_ip}",
                    role='cold',
                    ip=cold_ip,
                    version=deploy_info['version'],
                    device_class=device_class,
                    hard_memo=hard_memo,
                )
            for client_ip in deploy_info['client_list']:
                res = get_cc_info_by_ip(deploy_info['bk_username'], deploy_info['app_id'], client_ip)
                device_class = res['data']['info'][0].get('svr_device_class', 'Not Available')
                hard_memo = res['data']['info'][0].get('hard_memo', 'Not Available')

                EsNodeInfo.objects.create(
                    app_id=deploy_info['app_id'],
                    cluster_name=deploy_info['cluster_name'],
                    node_name=f"client-{client_ip}",
                    role='client',
                    ip=client_ip,
                    version=deploy_info['version'],
                    device_class=device_class,
                    hard_memo=hard_memo,
                )

            # 插入集群用户信息
            EsRule.objects.create(
                app=deploy_info['app'],
                app_id=deploy_info['app_id'],
                cluster_name=deploy_info['cluster_name'],
                user_name=deploy_info['account']
            )

    except Exception as err:
        logger.error(f"集群数据插入发生异常：{str(err)}")
        return None

    return cluster.id


def update_es_cluster(cluster_id, update_data):
    """
       更新es cluster的数据
       @param cluster_id: 集群id
       @param update_data:更新数据
    """
    try:
        EsCluster.objects.filter(id=cluster_id).update(**update_data)
        return True

    except Exception as err:
        logger.error(f"ES集群数据更新发生异常{str(err)}")
        return False


def delete_es_cluster(cluster_name):
    """
       清空对应es cluster的相关数据
       @param cluster_name: 集群id
    """
    try:
        # 绑定事务删除，保证事务的数据一致性
        with transaction.atomic():
            EsCluster.objects.filter(cluster_name=cluster_name).delete()
            EsNodeInfo.objects.filter(cluster_name=cluster_name).delete()
            EsRule.objects.filter(cluster_name=cluster_name).delete()
        return True

    except Exception as err:
        logger.error(f"ES集群数据删除发生异常{str(err)}")
        return False


def add_es_node(add_info):
    """
       扩容后插入新的进程信息
       @param add_info:{
            "app_id": 业务id,
            "app": 业务名称,
            "cluster_id": 扩容所在的集群id,
            "cluster_name": 扩容所在的集群名称,
            "version": 节点版本,
            "http_port":  es http 集群端口号,
            "target_ips": 扩容ip列表,
            "role": 扩容节点角色,
            "master_str": 集群master节点信息，已逗号隔开,
            "bk_username": 任务创建者,
            "task_type": 任务类型
       }
    """
    role = add_info['role']
    add_ips = add_info[f"{role}_list"]
    try:
        with transaction.atomic():
            update_data = {f'{role}_cnt': F(f'{role}_cnt') + len(add_ips)}
            EsCluster.objects.filter(id=add_info['cluster_id']).update(**update_data)
            for add_node_ip in add_ips:
                # 在配置平台获取IP的硬件信息
                res = get_cc_info_by_ip(add_info['bk_username'], add_info['app_id'], add_node_ip)
                device_class = res['data']['info'][0].get('svr_device_class', 'Not Available')
                hard_memo = res['data']['info'][0].get('hard_memo', 'Not Available')

                EsNodeInfo.objects.create(
                    app_id=add_info['app_id'],
                    cluster_name=add_info['cluster_name'],
                    node_name=f"{add_info['role']}-{add_node_ip}",
                    role=add_info['role'],
                    ip=add_node_ip,
                    version=add_info['version'],
                    device_class=device_class,
                    hard_memo=hard_memo,
                )
        return True

    except Exception as err:
        logger.error(f"ES集群新增节点插入发生异常: {str(err)}")
        return False


def reduce_es_node(reduce_info):
    """
       缩容后删除节点信息
       @param reduce_info: {
            "app_id": 业务id,
            "cluster_id": 集群id
            "cluster_name": 集群名称,
            "version": 版本号,
            "http_port": es http 集群端口号,
            "target_ips": 待删除ip,
            "master_str": 集群master节点信息，已逗号隔开,
            "bk_username": 任务创建者 ,
            "task_type": 任务类型
        }
    """
    try:
        with transaction.atomic():

            # 更新节点数量
            for reduce_ip in reduce_info['target_ips']:
                role = EsNodeInfo.objects.get(ip=reduce_ip).role
                update_data = {f'{role}_cnt': F(f'{role}_cnt') - 1}
                EsCluster.objects.filter(id=reduce_info['cluster_id']).update(**update_data)

            EsNodeInfo.objects.filter(ip__in=reduce_info['target_ips']).delete()
        return True

    except Exception as err:
        logger.error(f"ES集群数据更新发生异常{str(err)}")
        return False
