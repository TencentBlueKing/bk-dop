# -*- coding:utf-8 _*
from blueapps.utils.logger import logger_celery
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list
from common.utils.constant import HADOOP_PACKAGE_PATH, fast_transfer_file_common_kwargs
'''
@summary: 多对多节点公钥文件传输，为做免认证连接做准备
@usage:
'''


class PushNodeRsa(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        cluster_name = act_info['cluster_name']
        cluster_user = act_info['cluster_user']
        hosts_info = act_info['hosts_info']
        bk_username = act_info['bk_username']

        if len([info['ip'] for info in hosts_info if info['add'] == 1]) == 0:
            logger_celery.warning("该活动节点没有对应新的ip可以执行，正常返回")
            data.outputs.result_message = "skip"
            return True

        source_ips = [info['ip'] for info in hosts_info]
        target_ips = source_ips

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{cluster_name}节点之间推送公钥文件",
            "file_target_path": f"{HADOOP_PACKAGE_PATH}/ssh/",
            "file_source_list": [
                {
                    "file_list": [f"/home/{cluster_user}/.ssh/id_rsa.pub.*"],
                    "account": {"alias": "root"},
                    "server": {"ip_list": get_job_ip_list(source_ips)},
                }
            ],
            "target_server": {"ip_list": get_job_ip_list(target_ips)},
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


class PushNodeRsaComponent(Component):
    name = __name__
    code = 'push_node_rsa_action'
    bound_service = PushNodeRsa
