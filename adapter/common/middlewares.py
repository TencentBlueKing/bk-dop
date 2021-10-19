# -*- coding: utf-8 -*-
import re
import json

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from adapter.common.log import logger
from adapter.common.utils import html_escape, url_escape, texteditor_escape


class CheckXssMiddleware(MiddlewareMixin):
    """
    XSS攻击统一处理中间件
    """

    def process_view(self, request, view, args, kwargs):
        """
        请求参数统一处理
        """
        try:
            # 判断豁免权
            if getattr(view, "escape_exempt", False):
                return None
            # 判断豁免
            escape_type = None
            if getattr(view, "escape_texteditor", False):
                escape_type = "texteditor"
            elif getattr(view, "escape_url", False):
                escape_type = "url"
            # get参数转换
            request.GET = self.__escape_data(request.path, request.GET, escape_type)
            # post参数转换
            request.POST = self.__escape_data(request.path, request.POST, escape_type)
        except Exception as e:
            logger.exception(u"CheckXssMiddleware 转换失败！错误信息：%s" % e)
        return None

    def __escape_data(self, path, query_dict, escape_type=None):
        """
        GET/POST参数转义
        """
        data_copy = query_dict.copy()
        for _get_key, _get_value_list in data_copy.lists():
            new_value_list = []
            for _get_value in _get_value_list:
                new_value = _get_value
                # json串不进行转义
                try:
                    json.loads(_get_value)
                    is_json = True
                except Exception:
                    is_json = False
                # 转义新数据
                if not is_json:
                    if escape_type is None:
                        use_type = self.__filter_param(path, _get_key)
                    else:
                        use_type = escape_type
                    if use_type == "url":
                        new_value = url_escape(_get_value)
                    elif use_type == "texteditor":
                        new_value = texteditor_escape(_get_value)
                    else:
                        new_value = html_escape(_get_value)
                else:
                    new_value = html_escape(_get_value, True)
                new_value_list.append(new_value)
            data_copy.setlist(_get_key, new_value_list)
        return data_copy

    def __filter_param(self, path, param):
        """
        特殊path处理
        @param path: 路径
        @param param: 参数
        @return: 'url/texteditor'
        """
        use_url_paths, use_texteditor_paths = self.__filter_path_list()
        result = self.__check_escape_type(path, param, use_url_paths, "url")
        # 富文本内容过滤
        if result == "html":
            result = self.__check_escape_type(path, param, use_texteditor_paths, "texteditor")
        return result

    def __check_escape_type(self, path, param, check_path_list, escape_type):
        """
        判断过滤类型
        @param path: 请求Path
        @param param: 请求参数
        @param check_path_list: 指定类型Path列表
        @param escape_type: 判断过滤类型
        @param result_type: 结果类型
        """
        try:
            result_type = "html"
            for script_path, script_v in list(check_path_list.items()):
                is_path = re.match(r"^%s" % script_path, path)
                if is_path and param in script_v:
                    result_type = escape_type
                    break
        except Exception as e:
            logger.exception(u"CheckXssMiddleware 特殊path处理失败！错误信息%s" % e)
        return result_type

    def __filter_path_list(self):
        """
        特殊path注册
        注册格式：{'path1': [param1, param2], 'path2': [param1, param2]}
        """
        SITE_URL = settings.SITE_URL
        use_url_paths = {
            "%saccounts/login" % SITE_URL: ["next"],
            "%saccounts/login_page" % SITE_URL: ["req_url"],
            "%saccounts/login_success" % SITE_URL: ["req_url"],
            "%s" % SITE_URL: ["url"],
        }
        use_texteditor_paths = {}
        return (use_url_paths, use_texteditor_paths)
