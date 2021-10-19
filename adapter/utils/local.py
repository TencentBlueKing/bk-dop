# -*- coding: utf-8 -*-
"""
记录线程变量
"""
import uuid
import sys
from threading import local

from django.conf import settings

from adapter.exceptions import BaseException
from blueapps.utils import get_request

_local = local()


def activate_request(request, request_id=None):
    """
    激活request线程变量
    """
    if not request_id:
        request_id = str(uuid.uuid4())
    request.request_id = request_id
    _local.request = request
    return request


# def get_request():
#     """
#     获取线程请求request
#     """
#     try:
#         return _local.request
#     except AttributeError:
#         raise BaseException(u"request thread error!")


def get_request_id():
    """
    获取request_id
    """
    try:
        return get_request().request_id
    except Exception:
        return str(uuid.uuid4())


def get_request_username():
    """
    获取请求的用户名
    """
    username = ""
    try:
        username = get_request().user.username
    except Exception:
        pass
    finally:
        if not username and "celery" in sys.argv:
            username = "admin"
    return username


def get_request_app_code():
    """
    获取线程请求中的 APP_CODE
    """
    try:
        return get_request().META.get("HTTP_BK_APP_CODE", settings.APP_CODE)
    except Exception:
        return settings.APP_CODE


# def set_local_param(key, value):
#     """
#     设置自定义线程变量
#     """
#     setattr(_local, key, value)
#
#
# def del_local_param(key):
#     """
#     删除自定义线程变量
#     """
#     if hasattr(_local, key):
#         delattr(_local, key)
#
#
# def get_local_param(key, default=None):
#     """
#     获取线程变量
#     """
#     return getattr(_local, key, default)
