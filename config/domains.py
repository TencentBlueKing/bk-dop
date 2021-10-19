# -*- coding: utf-8 -*-
from django.conf import settings


API_ROOTS = [
    # 蓝鲸平台模块域名
    "BK_LOGIN_APIGATEWAY_ROOT",
    "BK_PAAS_APIGATEWAY_ROOT",
    "BK_AUTH_APIGATEWAY_ROOT",
    "CC_APIGATEWAY_ROOT",
    "CC_APIGATEWAY_ROOT_V2",
    "GSE_APIGATEWAY_ROOT",
    "TOF_APIGATEWAY_ROOT",
    "TOF3_APIGATEWAY_ROOT",
    "GSE_APIGATEWAY_ROOT_V2",
    "ESB_APIGATEWAY_ROOT_V2",
    "MONITOR_APIGATEWAY_ROOT",
    "USER_MANAGE_APIGATEWAY_ROOT",
    # 数据平台模块域名
    "ACCESS_APIGATEWAY_ROOT",
    "AUTH_APIGATEWAY_ROOT",
    "DATAQUERY_APIGATEWAY_ROOT",
    "DATABUS_APIGATEWAY_ROOT",
    "STOREKIT_APIGATEWAY_ROOT",
    "META_APIGATEWAY_ROOT",
    # 信息推送
    "CMSI_API_ROOT",
    "WECHAT_APIGATEWAY_ROOT",
    # 节点管理
    "BK_NODE_APIGATEWAY_ROOT",
    # LOG_SEARCH
    "LOG_SEARCH_APIGATEWAY_ROOT",
]

domain_module = "adapter.sites.{}.config.domains".format(settings.RUN_VER)
module = __import__(domain_module, globals(), locals(), ["*"])

for _root in API_ROOTS:
    try:
        locals()[_root] = getattr(module, _root)
    except Exception:
        pass

__all__ = API_ROOTS
