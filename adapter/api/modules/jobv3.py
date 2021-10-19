# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _JobV3Api(BaseApi):
    MODULE = _("JOBV3")

    def __init__(self):
        self.fast_execute_script = ProxyDataAPI(_("快速执行脚本"))
        self.fast_transfer_file = ProxyDataAPI(_("快速分发文件"))
        self.get_task_ip_log = ProxyDataAPI(_("获取任务执行记录"))
        self.get_job_instance_log = ProxyDataAPI(_("根据作业ID获取作业执行记录"))
        self.get_job_instance_ip_log = ProxyDataAPI(_("根据作业ID查询作业执行日志"))
        self.get_job_instance_status = ProxyDataAPI(_("根据作业ID查询作业执行状态"))


JobV3Api = _JobV3Api()
