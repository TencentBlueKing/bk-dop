# -*- coding:utf-8 _*-
import json
import time

from adapter.api import JobV3Api
from blueapps.utils.logger import logger
from common.utils.constant import bk_cloud_id, fast_execute_script_common_kwargs


'''
@summary: 利用sdk的方式来调用job平台分发作业,同步操作
@usage:
'''


def build_job_err_log_format(username, job_sdk_name, job_sdk_params, job_result):
    """
     定义django 调用job平台时日志打印格式(错误日志)
    """

    # 删除敏感信息，避免输出日志
    return '''
    job调用失败:
    操作人({})
    接口名称({})
    请求参数({})
    返回参数({})
    状态码({})
    '''.format(
        username, job_sdk_name, job_sdk_params, job_result, job_result['code']
    )


def build_job_exec_log_format(username, job_sdk_name, job_task_name):
    """
     定义django 调用job平台时日志打印格式(成功日志)
    """

    # 删除敏感信息，避免输出日志
    return '''
    job调用成功:
    操作人({})
    接口名称({})
    任务名称({})
    '''.format(
        username, job_sdk_name, job_task_name
    )


class JobExecutor(object):
    """
    Job执行封装类
    """

    def __init__(self, bk_username, ips_list):
        """初始化client"""
        self.bk_username = bk_username
        self.ip_list = ips_list

    def fast_execute_script(self, kwargs):
        """
        快速执行脚本
        """
        # shell 脚本内容需要base64编码
        kwargs.update(
            {
                "bk_username": self.bk_username,
            }
        )

        result = JobV3Api.fast_execute_script({**kwargs, **fast_execute_script_common_kwargs}, raw=True)
        if result["result"]:
            query_kwargs = {
                "job_instance_id": result["data"].get("job_instance_id"),
                "bk_biz_id": kwargs.get("bk_biz_id"),
            }
            result = self.get_task_result_status(query_kwargs)
            logger.info(build_job_exec_log_format(self.bk_username, 'fast_execute_script', kwargs['task_name']))
            return result
        else:
            logger.error(build_job_err_log_format(self.bk_username, 'fast_execute_script', kwargs, result))
            return None

    def fast_push_file(self, kwargs):
        """
        快速分发文件
        """

        kwargs.update(
            {"bk_username": self.bk_username,}
        )

        result = JobV3Api.fast_transfer_file(kwargs, raw=True)
        if result["result"]:
            query_kwargs = {
                "job_instance_id": result["data"].get("job_instance_id"),
                "bk_biz_id": kwargs.get("bk_biz_id"),
            }
            result = self.get_task_result_status(query_kwargs)
            logger.info(build_job_exec_log_format(self.bk_username, 'fast_push_file', kwargs['task_name']))
            return result
        else:
            logger.error(build_job_err_log_format(self.bk_username, 'fast_push_file', kwargs, result))
            return None

    def get_task_result_status(self, kwargs):
        """
        批量查询job任务结果
        """

        result = None
        result_message = {}

        kwargs.update(
            {"bk_username": self.bk_username}
        )

        for query_max_times in range(100):
            result = JobV3Api.get_job_instance_status(kwargs, raw=True)
            if result["result"]:
                is_finished = result["data"].get("finished")
                if is_finished:
                    # 获取脚本调用的返回结果
                    step_instance_id = result["data"].get("step_instance_list")[0]['step_instance_id']
                    kwargs['step_instance_id'] = step_instance_id
                    kwargs['bk_cloud_id'] = bk_cloud_id
                    result_message = self.get_task_ip_log(kwargs)

                    break
                time.sleep(2)
            # 执行中则继续轮询
            else:
                time.sleep(2)
        return result, json.dumps(result_message)

    def get_task_ip_log(self, kwargs):
        """
        根据业务实例id查询和IP信息查询对应作业执行日志结果
        """
        result_message = {}

        kwargs.update(
            {"bk_username": self.bk_username}
        )

        for ip in self.ip_list:
            query_kwargs = kwargs
            query_kwargs['ip'] = ip
            result = JobV3Api.get_job_instance_ip_log(query_kwargs, raw=True)
            if result["result"]:
                result_message[ip] = result["data"].get("log_content")
            else:
                logger.error('{}:{}'.format(ip, result["message"]))
        return result_message
