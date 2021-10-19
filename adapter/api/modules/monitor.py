# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import BaseApi, ProxyDataAPI


class _MonitorApi(BaseApi):
    MODULE = _("Monitor")

    def __init__(self):
        self.get_ts_data = ProxyDataAPI(_("获取时序数据"))
        self.create_custom_time_series = ProxyDataAPI(_("创建自定义指标"))
        self.delete_custom_time_series = ProxyDataAPI(_("删除自定义指标"))
        self.custom_time_series_detail = ProxyDataAPI(_("获取自定义指标信息"))
        self.metadata_get_data_id = ProxyDataAPI(_("查询一个数据源的ID 根据给定的数据源ID，返回这个结果表的具体信息"))


MonitorApi = _MonitorApi()
