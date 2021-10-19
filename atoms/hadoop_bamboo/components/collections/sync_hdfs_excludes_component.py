# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_host_str, get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs


'''
@summary:
       回收datanode节点流程的配置更改
       将待回收节点加入excludes文件，列入黑名单
       相关节点的hostname在includes文件移除
@usage:
'''


class RemoveDataDodeConfig(GeneralService):

    def execute(self, data, parent_data):
        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        hdfs_includes = act_info['hdfs_includes']
        hdfs_excludes = act_info['hdfs_excludes']
        bk_username = act_info['bk_username']
        hosts_info = act_info['hosts_info']
        recycle_datanode_ip_list = act_info['datanode']

        target_ips = [info['ip'] for info in hosts_info]

        remove_includes_str = get_host_str(recycle_datanode_ip_list, hosts_info)

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}集群datanode节点加入黑名单",
            "script_content":
                get_script('hadoop_bamboo/components/collections/script_templates/remove_datanode_config.sh'),
            "script_param": get_script_param([hdfs_includes, hdfs_excludes, remove_includes_str]),
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


class RemoveDataDodeConfigComponent(Component):
    name = 'RemoveDataDodeConfigComponent'
    code = 'remove_datanode_config_action'
    bound_service = RemoveDataDodeConfig
