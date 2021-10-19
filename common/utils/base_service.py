# -*- coding: utf-8 -*-

from abc import ABCMeta

from pipeline.core.flow.activity import Service, StaticIntervalGenerator

from adapter.api import JobV3Api
from blueapps.utils.logger import logger
from common.utils.common import bk_cloud_id


class GeneralService(Service, metaclass=ABCMeta):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(2)

    def schedule(self, data, parent_data, callback_data=None):
        act_info = data.get_one_of_inputs('act_info')
        bk_username = act_info['bk_username']
        app_id = act_info['app_id']

        if data.get_one_of_outputs('result_message') == 'skip':
            # 表示该节点已经内部跳过，不执行监听
            self.finish_schedule()
            return True

        # 控制是否读取任务正确时读取返回日志的变量，默认false
        is_read_success_message = act_info.get('is_read_success_message')
        if is_read_success_message is None:
            is_read_success_message = False

        target_ips = data.get_one_of_outputs('target_ips')
        job_instance_id = data.get_one_of_outputs('job_instance_id')

        kwargs = {
            "bk_biz_id": app_id,
            "bk_username": bk_username,
            "job_instance_id": job_instance_id,
            "return_ip_result": True,
        }
        res = JobV3Api.get_job_instance_status(kwargs, raw=True)
        if not res['result']:
            return False

        if res['data']['finished']:
            self.finish_schedule()
            step_instance_id = res["data"].get("step_instance_list")[0]['step_instance_id']
            kwargs['step_instance_id'] = step_instance_id
            kwargs['bk_cloud_id'] = bk_cloud_id

            if res["data"].get("job_instance").get("status") == 3:
                # job任务执行成功
                if is_read_success_message:
                    data.outputs.result_message = self.__get_task_ip_log(kwargs=kwargs, target_ips=target_ips)
                else:
                    data.outputs.result_message = "success"
            else:
                # job结束后status不等于3 视为调用失败
                data.outputs.result_message = self.__get_task_ip_log(kwargs=kwargs, target_ips=target_ips)
                return False

        return True

    @staticmethod
    def __get_task_ip_log(kwargs, target_ips):
        """
        根据业务实例id查询和IP信息查询对应作业执行日志结果
        """
        result_message = {}
        for ip in target_ips:
            query_kwargs = kwargs
            query_kwargs['ip'] = ip
            result = JobV3Api.get_job_instance_ip_log(query_kwargs, raw=True)
            if result["result"]:
                result_message[ip] = result["data"].get("log_content")
            else:
                logger.error('{}:{}'.format(ip, result["message"]))
        return result_message
