# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from blueapps.utils.logger import logger_celery
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs


'''
@summary: 为了方便集群的管理，针对进程启动用户，对hadoop集群每个节点做免认证
@usage:
'''


class CreateAuthFreeLogin(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        cluster_user = act_info['cluster_user']
        cluster_name = act_info['cluster_name']
        hosts_info = act_info['hosts_info']
        bk_username = act_info['bk_username']

        if len([info['ip'] for info in hosts_info if info['add'] == 1]) == 0:
            logger_celery.warning("该活动节点没有对应新的ip可以执行，正常返回")
            data.outputs.result_message = "skip"
            return True

        target_ips = [info['ip'] for info in hosts_info]

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{cluster_name}集群各节点添加免认证",
            "script_content":
                get_script('hadoop_bamboo/components/collections/script_templates/create_authentication_free_login.sh'),
            "script_param": get_script_param([cluster_user]),
            "target_server": {"ip_list": get_job_ip_list(target_ips)},
        }

        res = JobV3Api.fast_execute_script({**kwargs, **fast_execute_script_common_kwargs}, raw=True)
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


class CreateAuthFreeLoginComponent(Component):
    name = __name__
    code = 'create_auth_free_login_action'
    bound_service = CreateAuthFreeLogin
