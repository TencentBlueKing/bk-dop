# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs
from blueapps.utils.logger import logger

'''
@summary: 初始化hadoop集群的 namenode 和 zkfc 的配置信息,并启动namenode和zkfc节点
@usage:
'''


class StartNameNode(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')
        node_name = data.get_one_of_inputs('node_name')

        app_id = act_info['app_id']
        cluster_user = act_info['cluster_user']
        base_dir = act_info['base_dir']
        name_node_ip_list = act_info['namenode']
        standby_name_node_ip_list = act_info['standbynamenode']
        bk_username = act_info['bk_username']

        if node_name == 'namenode':
            target_ips = name_node_ip_list
        elif node_name == 'standbynamenode':
            target_ips = standby_name_node_ip_list
        else:

            data.outputs.result_message = 'fail'
            return False

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}集群新{node_name}节点启动",
            "script_content":
                get_script('hadoop_bamboo/components/collections/script_templates/start_namenode_server.sh'),
            "script_param": get_script_param([cluster_user, base_dir, node_name, target_ips[0]]),
            "target_server": {"ip_list": get_job_ip_list(target_ips)},
        }

        res = JobV3Api.fast_execute_script({**kwargs, **fast_execute_script_common_kwargs}, raw=True)
        if not res['result']:
            logger.error(f"无法识别到部署节点类型{node_name}")
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
        ]

    def outputs_format(self):
        return [

            Service.OutputItem(name='job_instance_id', key='job_instance_id', type='int'),
            Service.OutputItem(name='result_message', key='result_message', type='str'),
            Service.OutputItem(name='target_ips', key='target_ips', type='list')
        ]


class StartNameNodeComponent(Component):
    name = __name__
    code = 'start_name_node_action'
    bound_service = StartNameNode
