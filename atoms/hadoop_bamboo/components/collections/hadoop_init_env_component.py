# -*- coding:utf-8 _*-
from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from blueapps.utils.logger import logger_celery
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list, get_script, get_script_param
from common.utils.constant import HADOOP_PACKAGE_PATH, fast_execute_script_common_kwargs, hadoop_package_full_name_dict


'''
@summary: hadoop部署集群之前初始化每个节点的部署环境和推送配置。
@usage:
'''


class InitBeforeDeploy(GeneralService):

    def execute(self, data, parent_data):

        act_info = data.get_one_of_inputs('act_info')

        app_id = act_info['app_id']
        bk_username = act_info['bk_username']
        hosts_info = act_info['hosts_info']
        cluster_version = act_info['cluster_version']
        cluster_user = act_info['cluster_user']
        base_dir = act_info['base_dir']
        data_disk_dir_list = act_info['data_disk_dir_list']

        java_file = "{}/java-{}.tar.gz".format(
            HADOOP_PACKAGE_PATH, hadoop_package_full_name_dict[cluster_version]["java"]["version"]
        )
        hadoop_file = "{}/hadoop-{}.tar.gz".format(
            HADOOP_PACKAGE_PATH, hadoop_package_full_name_dict[cluster_version]["hadoop"]["version"]
        )
        zookeeper_file = "{}/zookeeper-{}.tar.gz".format(
            HADOOP_PACKAGE_PATH, hadoop_package_full_name_dict[cluster_version]["zookeeper"]["version"]
        )

        # 解决shell数组遍历问题，没有字符串都需要加'' 来封装来传递
        hadoop_data_str = ",".join(data_disk_dir_list)

        dns_hosts_list = []
        for host in hosts_info:
            ip = host.get("ip")
            host_name = host.get("host_name")
            dns_hosts_list.append("'{}:{}'".format(ip, host_name))
        dns_hosts_str = ",".join(dns_hosts_list)

        target_ips = [info['ip'] for info in hosts_info if info['add'] == 1]

        if len(target_ips) == 0:
            logger_celery.warning("该活动节点没有对应新的ip可以执行，正常返回")
            data.outputs.result_message = "skip"
            return True

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "task_name": f"{act_info['cluster_name']}集群新节点初始化过程",
            "script_content": get_script('hadoop_bamboo/components/collections/script_templates/init_before_deploy.sh'),
            "script_param": get_script_param([
                cluster_user,
                base_dir,
                hadoop_file,
                java_file,
                zookeeper_file,
                hadoop_data_str,
                dns_hosts_str
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


class InitBeforeDeployComponent(Component):
    name = __name__
    code = 'init_before_deploy_action'
    bound_service = InitBeforeDeploy
