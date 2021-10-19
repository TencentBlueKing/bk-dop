# -*- coding: utf-8 -*-

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs


class InstallHadoopMonitorService(GeneralService):
    def execute(self, data, parent_data):
        act_info = data.get_one_of_inputs('act_info')
        bk_username = act_info['bk_username']
        app_id = act_info['app_id']
        target_ips = act_info['target_ips']
        target_ips_str = ",".join(target_ips)
        bk_data_id = str(act_info['bk_data_id'])
        access_token = act_info['access_token']
        metric_port = str(act_info['metric_port'])
        cluster_name = act_info['cluster_name']

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "script_content": get_script('hadoop_bamboo/components/collections/script_templates/init_monitor.sh'),
            "script_param": get_script_param([bk_data_id, access_token, metric_port, target_ips_str, cluster_name]),
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


class InstallHadoopMonitorComponent(Component):
    name = __name__
    code = 'install_hadoop_monitor_action'
    bound_service = InstallHadoopMonitorService
