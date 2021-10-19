# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs


'''
@summary: 管控yarn集群节点，管控操作：启动(start)，关闭(stop)，重启(restart)
@usage:
'''


class StartYarnNode(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')
        node_name = data.get_one_of_inputs('node_name')
        ops = data.get_one_of_inputs('ops')

        app_id = act_info['app_id']
        base_dir = act_info['base_dir']
        cluster_user = act_info['cluster_user']
        cluster_version = act_info['cluster_version']
        bk_username = act_info['bk_username']
        target_ips = act_info[node_name]

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}集群yarn集群启动",
            "script_content": get_script('hadoop_bamboo/components/collections/script_templates/yarn_ops.sh'),
            "script_param": get_script_param([base_dir, cluster_user, ops, node_name, cluster_version]),
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
            Service.InputItem(name='node_name', key='node_name', type='str', required=True),
            Service.InputItem(name='ops', key='ops', type='str', required=True),
        ]

    def outputs_format(self):
        return [

            Service.OutputItem(name='job_instance_id', key='job_instance_id', type='int'),
            Service.OutputItem(name='result_message', key='result_message', type='str'),
            Service.OutputItem(name='target_ips', key='target_ips', type='list')
        ]


class StartYarnNodeComponent(Component):
    name = __name__
    code = 'start_yarn_node_action'
    bound_service = StartYarnNode
