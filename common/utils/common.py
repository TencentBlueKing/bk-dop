# -*- coding:utf-8 _*-
import base64
import os
import re
import time

from django.db.models import Count

from adapter.api import CCApi
from blueapps.utils.logger import logger
from common.utils.constant import bk_cloud_id
from config import BASE_DIR


ATOM_DIR = os.path.join(BASE_DIR, 'atoms')

'''
@summary: 定义公关函数，减少重复代码
@usage:
'''


def build_fail_result(message):
    """
       组装返回前端返回错误参数
       返回格式：
       {
       "code":
       "data":{ "result":xxx, "data":[], "message":xxx , "code": xxx }
       }
    """
    return {"code": 0, "data": {"result": False, "data": [], "message": "{}".format(message), "code": 1}}


def build_success_result(message):
    """
       组装返回前端返回正确参数
       返回格式：
       {
       "code":
       "data":{ "result":xxx, "data":[], "message":xxx , "code": xxx }
       }
    """
    return {"code": 1, "data": {"result": True, "data": [], "message": "{}".format(message), "code": 0}}


def str_trans_list(conf_str):
    """
      根据前端传入的字符串来进行分割，生成标准的列表形式,并且去重和去掉多余的空格项
    """
    try:
        if isinstance(conf_str, list):
            # 如果存入的list数组，则不需要进一步修饰，兼容任务重试参数返回list的情况
            return conf_str

        res = re.compile(r'''[\n\s\t;,'"]+''')
        conf_list = list(set(res.split(conf_str)))
        return list(filter(None, conf_list))

    except Exception as err:
        logger.error(str(err))
        return []


def is_ip(ip_str):
    """
       判断是否合法ip
    """
    p = re.compile(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    return p.match(ip_str)


def is_dir(dir_str):
    """
       判断是否合法的绝对路径
    """
    # p = re.compile(r'^/(\w+/?)+$')
    p = re.compile(r'^/[-\w./?]+$')
    return p.match(dir_str)


def get_job_ip_list(ip_list):
    """
       1：根据job平台调格式，拼写针对适配参数的格式
       2：针对性优化，便于后续变更和减少代码重复量
       3：格式：[{"bk_cloud_id":0, "ip":"1.1.1.1" }]
    """
    target_ips = []
    for ip in ip_list:
        ip_dict = {"bk_cloud_id": bk_cloud_id, "ip": ip}
        target_ips.append(ip_dict)
    return target_ips


def get_cc_info_by_ip(bk_username, app_id, ip):
    """
       根据ip和业务id获取ip的硬件信息
    """
    kwargs = {
        "bk_biz_id": app_id,
        "bk_username": bk_username,
        "fields": ["bk_host_innerip", "hard_memo", "svr_device_class"],
        "host_property_filter": {
            "condition": "AND",
            "rules": [{"field": "bk_host_innerip", "operator": "equal", "value": ip}],
        },
        "page": {"start": 0, "limit": 10, "sort": "bk_host_id"},
    }
    res = CCApi.list_biz_hosts(kwargs, raw=True)
    return res


def get_cc_app_id_by_user(res='print_id'):
    """
       获取用户的已有权限的业务信息id
       @param res: 控制输出格式，如果是print_id格式，则输出app_id 列表； 如果是print_name格式，则输出 app_id: app_name 的 数组内容
    """
    app_id_list = []
    app_id_dict = {}
    try:
        kwargs = {
            "fields": ["bk_biz_id", "bk_biz_name"],
        }
        get_app_result = CCApi.search_business(kwargs, raw=True)
        if not get_app_result["result"]:
            return None
        if res == 'print_name':
            for app_info in get_app_result["data"]["info"]:
                app_id_dict[app_info['bk_biz_id']] = app_info['bk_biz_name']
            return app_id_dict

        app_id_list = [app_id["bk_biz_id"] for app_id in get_app_result["data"]["info"]]
        return app_id_list

    except Exception as err:
        logger.error(f"获取用户权限失败：报错信息:{str(err)}")
        return app_id_list


def get_script(script_path):
    """
       获取对应脚本内容，按照base64编码输出
    """
    script = open(os.path.join(ATOM_DIR, script_path)).read()
    return base64.b64encode(str.encode(script)).decode(encoding="utf-8")


def get_script_param(script_param_list):
    """
       获取对应脚本的参数组，按照base64编码输出
    """
    param = " ".join(script_param_list)
    return base64.b64encode(str.encode(param)).decode(encoding="utf-8")


def create_host_name(cluster_name, ip_str):
    """
       hadoop部署专属
       平台自动生成hostname信息
       通过合法ip和集群名称来生成对应的hostname名称。
       生成规则：集群名称-hadoop-ip信息()

    """
    ip_str = ip_str.replace('.', '-')

    return "{}-hadoop-{}".format(cluster_name, ip_str)


def find_host_name(hostname_list, ip_str):
    """
       hadoop录入集群专属功能
       通过前端返回的域名映射数组，来寻找指定ip的域名信息
       前端返回域名映射元素规则：'hostname/ip'
    """
    for hostname_info in hostname_list:
        ip = hostname_info.split("/")[0]
        hostname = hostname_info.split("/")[1]
        if ip_str == ip:
            # 匹配通过立即返回对应的hostname信息
            return hostname

    # 如果匹配不到则返回none
    return None


def get_host_str(ip_list, info_list):
    """
       hadoop专属
       1: 根据传进来的ip列表和初始化信息做对比，获取对应的hostname列表，并生成对应字符串，用","隔开
       2：针对性优化，减少代码重复量
    """
    hostname_list = []
    for ip in ip_list:
        for info in info_list:
            if ip == info['ip']:
                hostname_list.append(info['host_name'])
                break
    if hostname_list:
        return ",".join(hostname_list)
    else:
        return ""


def machine_statistics(table_set, field, app_id_list):
    """
       orm 方法统计机器数量
       @param app_id_list: 用户的业务权限列表
       @param table_set: 传递的表集合
       @param field : 指定聚合的字段名称
    """
    try:
        distinct_query = table_set.objects.filter(
            app_id__in=app_id_list).aggregate(
            value=Count(f'{field}', distinct=True))
        return str(distinct_query['value'])

    except Exception as err:
        logger.error(str(err))
        return '0'


def machine_statistics_group_app_id_top_five(table_set, field, app_dict):
    """
       orm 方法：根据用户权限的业务id，来统计每个业务的集群资源投入情况，输出top5
       @param app_dict: 用户的业务权限字典
       @param table_set: 传递的表集合
       @param field : 指定聚合的字段名称
    """
    app_id_list = list(app_dict.keys())
    try:
        annotate_query = table_set.objects.filter(
            app_id__in=app_id_list).values('app_id').annotate(
            value=Count(f'{field}', distinct=True)).order_by('-value')[:5]

        return [
            {
                "value": query.get("value"),
                "name": app_dict.get(query.get("app_id")) if app_dict.get(query.get("app_id")) else "未知业务",
            }
            for query in annotate_query
        ]
    except Exception as err:
        logger.error(str(err))
        return []


def find_last_monitor_data(metric_list):
    # 查询最新时间的监控维度值
    last_time = 0
    last_item = {}
    if metric_list:
        for item in metric_list:
            if item.get('time') > last_time:
                last_item = item

    return last_item


def compute_metrics_trans(metric_list, metric_name_list, convert_type=None, is_rate=False):
    # 查询维度值做对应转换
    if convert_type == 'K':
        divisor = 1024
    elif convert_type == 'M':
        divisor = 1024 * 1024
    elif convert_type == 'G':
        divisor = 1024 * 1204 * 1024
    else:
        divisor = 1

    rate_list = []
    if is_rate:
        # 需要做增量计算
        for i in range(0, len(metric_list)):
            error_tag = False
            current = metric_list[i]
            old = metric_list[i - 1]
            tmp = {"time": time.strftime("%m/%d %H:%M", time.localtime(float(current.get("time")) / 1000))}

            for metric_name in metric_name_list:
                if i == 0 or metric_list[i].get(metric_name) is None or metric_list[i - 1].get(metric_name) is None:
                    error_tag = True
                    continue
                tmp[f"{metric_name}_rate"] = round((current.get(metric_name) - old.get(metric_name)) / divisor, 2)

            if not error_tag:
                rate_list.append(tmp)

    else:
        # 做时间和单位倍率转换
        for item in metric_list:
            tmp = {'time': time.strftime("%m/%d %H:%M", time.localtime(float(item.get("time")) / 1000))}
            for metric_name in metric_name_list:
                tmp[metric_name] = round(item.get(metric_name) / divisor, 2)

            rate_list.append(tmp)

    return rate_list
