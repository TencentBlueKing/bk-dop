# -*- coding:utf-8 _*-

from bamboo_engine import api
from pipeline.eri.runtime import BambooDjangoRuntime

from blueapps.utils.logger import logger


'''
@summary:定义操作bamboo-engine类，对异步任务做管理操作
@usage:
'''


class PipelineTaskApi(object):
    """
        定义bamboo-engine的task管理操作
        支持task运行；重试；撤销；删除等相关操作
    """

    def __init__(self, kwargs):
        self.pipeline_id = kwargs.get("pipeline_id", "")
        self.node_id = kwargs.get("node_id", "")

    def task_pause(self):
        """
           手动暂停正在运行的pipeline任务
        """
        pause_info = api.pause_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_id)
        if not pause_info.result:
            logger.error("暂停任务失败,错误信息:{}，pipeline_id :{}".format(pause_info.exc, self.pipeline_id))
        return pause_info.result

    def task_revoke(self):
        """
           手动撤销pipeline任务
        """
        revoke_info = api.revoke_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_id)
        if not revoke_info.result:
            logger.error("撤销任务失败,错误信息:{}，pipeline_id :{}".format(revoke_info.exc, self.pipeline_id))
        return revoke_info.result

    def task_resume(self):
        """
            手动启动已暂停的pipeline任务
        """
        resume_info = api.resume_pipeline(runtime=BambooDjangoRuntime(), pipeline_id=self.pipeline_id)
        if not resume_info.result:
            logger.error("重新启动任务失败,错误信息:{}，pipeline_id :{}".format(resume_info.exc, self.pipeline_id))
        return resume_info.result

    def task_retry(self):
        """
            手动重试已失败的pipeline任务
        """
        retry_info = api.retry_node(runtime=BambooDjangoRuntime(), node_id=self.node_id)
        if not retry_info.result:
            logger.error("重试失败节点失败,错误信息:{}，pipeline_id :{}".format(retry_info.exc, self.node_id))
        return retry_info.result

    def get_task_states(self):
        """
            根据pipeline_id 获取流程树状态
        """
        if self.pipeline_id:
            data = api.get_pipeline_states(runtime=BambooDjangoRuntime(), root_id=self.pipeline_id).data
            return data
        else:
            return None

    def get_node_output(self):
        """
           根据node_id 获取活动节点的输出日志
        """
        if self.node_id:
            data = api.get_execution_data_outputs(runtime=BambooDjangoRuntime(), node_id=self.node_id).data.get(
                'result_message', 'running'
            )
            return data
        else:
            logger.error("no node_id")
            return None

    def get_node_job_id(self):
        """
            根据node_id 获取活动节点的job的job_instance_id
        """
        if self.node_id:
            data = api.get_execution_data_outputs(runtime=BambooDjangoRuntime(), node_id=self.node_id).data.get(
                'job_instance_id'
            )
            return data
        else:
            logger.error("no node_id")
            return None
