# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_host_str, get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs

'''
@summary: 更新hdfs的include文件配置(datanode和yarn兼容)
@usage:
'''


class AddIncludeConfig(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        hdfs_includes = act_info['hdfs_includes']
        hdfs_excludes = act_info['hdfs_excludes']
        bk_username = act_info['bk_username']
        hosts_info = act_info['hosts_info']

        target_ips = [info['ip'] for info in hosts_info]

        add_includes_str = get_host_str([info['ip'] for info in hosts_info if info['process_add'] == 1], hosts_info)

        dns_hosts_list = []
        dns_hosts_str = ""
        for host in hosts_info:
            if host['add'] == 1:
                dns_hosts_list.append("'{}:{}'".format(host.get("ip"), host.get("host_name")))
            dns_hosts_str = ",".join(dns_hosts_list)

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}更新hdfs的include文件配置",
            "script_content":
                get_script('hadoop_bamboo/components/collections/script_templates/update_include_config.sh'),
            "script_param": get_script_param([hdfs_includes, hdfs_excludes, add_includes_str, dns_hosts_str]),
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


class AddIncludeConfigComponent(Component):
    name = 'AddIncludeConfigComponent'
    code = 'add_include_config_action'
    bound_service = AddIncludeConfig
