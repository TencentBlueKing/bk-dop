# -*- coding: utf-8 -*-

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs, ES_ADMIN, ES_ADMIN_PASSWORD


class InstallEsService(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')
        role = data.get_one_of_inputs('role')

        bk_username = act_info['bk_username']
        app_id = act_info['app_id']
        cluster_name = act_info['cluster_name']
        master_str = act_info['master_str']
        http_port = act_info['http_port']
        version = act_info['version']
        target_ips = act_info['master_list'] if (act_info.get('spec') == 'mixed') else act_info[f'{role}_list']
        es_user = ES_ADMIN
        es_password = ES_ADMIN_PASSWORD

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "script_content": get_script('es_bamboo/components/collections/script_templates/install_es.sh'),
            "script_param": get_script_param([cluster_name, master_str, role, http_port, version, es_user, es_password]),
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
            Service.InputItem(name='role', key='role', type='string', required=True),
        ]

    def outputs_format(self):
        return [

            Service.OutputItem(name='job_instance_id', key='job_instance_id', type='int'),
            Service.OutputItem(name='result_message', key='result_message', type='str'),
            Service.OutputItem(name='target_ips', key='target_ips', type='list')
        ]


class InstallEsComponent(Component):
    name = __name__
    code = 'install_es_action'
    bound_service = InstallEsService
