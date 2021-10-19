# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from adapter.api.base import DataAPI
from adapter.sites.open.config.domains import MONITOR_APIGATEWAY_ROOT


def get_monitor_request_before(params):
    return params


class _MonitorApi(object):
    MODULE = _("Monitor")

    def __init__(self):
        self.get_ts_data = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "get_ts_data",
            description=_("获取时序数据"),
            module=self.MODULE,
            before_request=get_monitor_request_before,
        )
        self.create_custom_time_series = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "create_custom_time_series",
            description=_("创建自定义指标"),
            module=self.MODULE,
            before_request=get_monitor_request_before,
        )
        self.delete_custom_time_series = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "delete_custom_time_series",
            description=_("删除自定义指标"),
            module=self.MODULE,
            before_request=get_monitor_request_before,
        )
        self.custom_time_series_detail = DataAPI(
            method="POST",
            url=MONITOR_APIGATEWAY_ROOT + "custom_time_series_detail",
            description=_("获取自定义指标信息"),
            module=self.MODULE,
            before_request=get_monitor_request_before,
        )
        self.metadata_get_data_id = DataAPI(
            method="GET",
            url=MONITOR_APIGATEWAY_ROOT + "metadata_get_data_id",
            description=_("查询一个数据源的ID 根据给定的数据源ID，返回这个结果表的具体信息"),
            module=self.MODULE,
            before_request=get_monitor_request_before,
        )


MonitorApi = _MonitorApi()
