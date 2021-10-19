# -*- coding: utf-8 -*-
import os
import time

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script
from common.utils.constant import fast_execute_script_common_kwargs


class SearchGuardInit(GeneralService):

    def execute(self, data, parent_data):
        act_info = data.get_one_of_inputs('act_info')

        bk_username = act_info['bk_username']
        app_id = act_info['app_id']
        target_ips = [act_info['master_list'][0]]

        # 等待es进程拉起
        time.sleep(80)

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "script_content": get_script('es_bamboo/components/collections/script_templates/search_guard_init.sh'),
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


class SearchGuardInitComponent(Component):
    name = __name__
    code = 'search_guard_init_action'
    bound_service = SearchGuardInit
