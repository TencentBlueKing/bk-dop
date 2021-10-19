# -*- coding:utf-8 _*-

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs

'''
@summary: 更新hdfs的hdfs文件配置的多盘策略,配置立即生效,但不主动平衡数据,需要用户在合适时间手动执行
@usage:
'''


class DataNodeReConfigDir(GeneralService):

    def execute(self, data, parent_data):
        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        cluster_user = act_info['cluster_user']
        base_dir = act_info['base_dir']
        bk_username = act_info['bk_username']
        hosts_info = act_info['hosts_info']
        add_dir_str = ",".join(act_info['scaled_up_dir_list'])
        new_dir_str = "{},{}".format(act_info['old_dir_str'], add_dir_str)

        target_ips = [info['ip'] for info in hosts_info]

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}更新hdfs的数据目录配置",
            "script_content":
                get_script('hadoop_bamboo/components/collections/script_templates/update_data_node_dir.sh'),
            "script_param": get_script_param([cluster_user, base_dir, new_dir_str]),
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


class DataNodeReConfigDirComponent(Component):
    name = __name__
    code = 'datanode_re_config_dir_action'
    bound_service = DataNodeReConfigDir
