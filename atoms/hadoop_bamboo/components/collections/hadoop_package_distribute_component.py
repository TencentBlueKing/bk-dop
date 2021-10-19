# -*- coding:utf-8 _*
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from blueapps.utils.logger import logger_celery
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list
from common.utils.constant import (
    HADOOP_PACKAGE_PATH,
    fast_transfer_file_common_kwargs,
    hadoop_package_full_name_dict,
    package_source_ip_list,
)


'''
@summary: HDFS的文件分发组件，包括java安装包，hadoop安装包，zookeeper安装
@usage:
'''


class HdfsPackageDistribute(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        hosts_info = act_info['hosts_info']
        cluster_version = act_info['cluster_version']
        bk_username = act_info['bk_username']

        target_ips = [info['ip'] for info in hosts_info if info['add'] == 1]

        if len(target_ips) == 0:
            logger_celery.warning("该活动节点没有对应新的ip可以执行，正常返回")
            data.outputs.result_message = "skip"
            return True

        package_full_name_list = (
            [hadoop_package_full_name_dict[cluster_version]["hadoop"]["package"]]
            + [hadoop_package_full_name_dict[cluster_version]["java"]["package"]]
            + [hadoop_package_full_name_dict[cluster_version]["zookeeper"]["package"]]
        )

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}集群新节点安装包分发过程",
            "file_target_path": HADOOP_PACKAGE_PATH,
            "file_source_list": [
                {
                    "file_list": package_full_name_list,
                    "account": {"alias": "root"},
                    "server": {"ip_list": package_source_ip_list},
                }
            ],
            "target_server": {"ip_list": get_job_ip_list(target_ips)},
            'account_alias': 'root',
        }

        res = JobV3Api.fast_transfer_file({**kwargs, **fast_transfer_file_common_kwargs}, raw=True)
        if not res['result']:
            # 调用job任务失败，则结果直接输出fail给前端展示
            data.outputs.result_message = 'fail'
        else:
            job_instance_id = res['data']['job_instance_id']
            data.outputs.job_instance_id = job_instance_id
            data.outputs.target_ips = target_ips
        return res['result']

    def inputs_format(self):
        return [
            Service.InputItem(name='dict action_info', key='act_info', type='dict', required=True),
        ]

    def outputs_format(self):
        return [

            Service.OutputItem(name='job_instance_id', key='job_instance_id', type='int'),
            Service.OutputItem(name='result_message', key='result_message', type='str'),
            Service.OutputItem(name='target_ips', key='target_ips', type='list')
        ]


class HdfsPackageDistributeComponent(Component):
    name = __name__
    code = 'package_distribute_action'
    bound_service = HdfsPackageDistribute
