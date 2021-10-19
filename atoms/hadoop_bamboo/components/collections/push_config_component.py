# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_host_str, get_job_ip_list, get_script, get_script_param
from common.utils.constant import fast_execute_script_common_kwargs


'''
@summary: 生成hdfs对应的配置文件
@usage:
'''


class PushConfig(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        cluster_user = act_info['cluster_user']
        base_dir = act_info['base_dir']
        hdfs_includes = act_info['hdfs_includes']
        hdfs_excludes = act_info['hdfs_excludes']
        hosts_info = act_info['hosts_info']
        bk_username = act_info['bk_username']
        replication_number = str(act_info['replication_number'])
        zookeeper_list = act_info['zookeepernode']
        journal_list = act_info['journalnode']
        namenode_list = act_info['namenode']
        standynamenode_list = act_info['standbynamenode']
        datanode_list = act_info['datanode']
        resourcemanger_list = act_info['resourcemanager']
        nodemanger_list = act_info['nodemanager']
        data_dir_str = ",".join(act_info['data_disk_dir_list'])
        ops_type = act_info['ops_type']

        # 生成hostname列表
        zookeeper_hostname_str = get_host_str(zookeeper_list, hosts_info)
        journal_hostname_str = get_host_str(journal_list, hosts_info)
        namenode_hostname_str = get_host_str(namenode_list, hosts_info)
        standynamenode_hostname_str = get_host_str(standynamenode_list, hosts_info)
        datanode_hostname_str = get_host_str(datanode_list, hosts_info)
        resourcemangerhostname_str = get_host_str(resourcemanger_list, hosts_info)
        nodemanger_hostname_str = get_host_str(nodemanger_list, hosts_info)

        target_ips = [info['ip'] for info in hosts_info if info['process_add'] == 1]

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}集群新节点推送配置过程",
            "script_content": get_script('hadoop_bamboo/components/collections/script_templates/push_config.sh'),
            "script_param": get_script_param([
                cluster_user,
                base_dir,
                hdfs_includes,
                hdfs_excludes,
                zookeeper_hostname_str,
                journal_hostname_str,
                namenode_hostname_str,
                standynamenode_hostname_str,
                datanode_hostname_str,
                data_dir_str,
                replication_number,
                ops_type,
                resourcemangerhostname_str,
                nodemanger_hostname_str,
            ]),
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


class PushConfigComponent(Component):
    name = __name__
    code = 'push_config_action'
    bound_service = PushConfig
