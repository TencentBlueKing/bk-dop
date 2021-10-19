# -*- coding: utf-8 -*-
import base64

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service

from adapter.api import JobV3Api
from common.utils.base_service import GeneralService
from common.utils.common import get_job_ip_list
from common.utils.constant import ES_ADMIN, ES_ADMIN_PASSWORD, fast_execute_script_common_kwargs


class EsGrantService(GeneralService):
    def execute(self, data, parent_data):
        act_info = data.get_one_of_inputs('act_info')
        bk_username = act_info['bk_username']
        app_id = act_info['app_id']

        account = act_info['account']
        password = act_info['password']
        version = act_info['version']
        target_ips = [act_info['master_list'][0]]
        http_port = act_info['http_port']

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "script_content": self.__search_guard_init_script(
                version=version,
                superuser=ES_ADMIN,
                super_password=ES_ADMIN_PASSWORD,
                account=account,
                password=password,
                http_port=http_port,),
            "target_server": {
                "ip_list": get_job_ip_list(target_ips)},
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

    @staticmethod
    def __search_guard_init_script(version, superuser, super_password, account, password, http_port):
        script = ""
        if version == "5.4.0":
            script = """
                #!/bin/bash
                sleep 80
                cd /data/esenv/es/plugins/search-guard/tools && bash init.sh yes
            """
        if version[0:1] == "7":
            script = """
            sleep 80
            curl -u'%s:%s' -H "Content-Type: application/json" -XPUT \
            http://localhost:%s/_opendistro/_security/api/internalusers/%s -d '{
            "password": "%s", "backend_roles": ["admin"] }'""" % (
                superuser,
                super_password,
                http_port,
                account,
                password,
            )

        if version[0:1] == "6":
            script = """
                sleep 80
                curl -u'%s:%s' -H "Content-Type: application/json" -XPUT \
                http://localhost:%s/_opendistro/_security/api/internalusers/"%s -d'{
                    "password": "%s",
                    "roles": ["admin"]
                }'
            """ % (
                superuser,
                super_password,
                http_port,
                account,
                password,
            )
        return base64.b64encode(str.encode(script)).decode(encoding="utf-8")


class EsGrantComponent(Component):
    name = __name__
    code = 'es_grant_action'
    bound_service = EsGrantService
