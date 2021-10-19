# -*- coding:utf-8 -*-

from adapter.api import MonitorApi
from blueapps.utils.logger import logger


class MonitorExecutor(object):
    """
        monitor api操作封装
    """

    def __init__(self, bk_username):
        """
           初始化client
        """
        self.bk_username = bk_username

    def get_monitor_data(self, sql):
        """
           获取监控平台数据
        """

        get_result = MonitorApi.get_ts_data({
            'bk_username': self.bk_username,
            'sql': sql
        })
        return get_result.get('list')

    def create_monitor_data(self, app_id, monitor_name):
        """
           部署监控自定义指标，获取对应的data_id 和 access_token
        """
        for monitor_id in range(1, 10000):
            logger.info(monitor_id)
            try:
                result = MonitorApi.create_custom_time_series({
                    'bk_username': self.bk_username,
                    'bk_biz_id': app_id,
                    'name': f'{monitor_name}_{monitor_id}',
                    'scenario': 'host_process'
                })
                info = MonitorApi.custom_time_series_detail({
                    'bk_username': self.bk_username,
                    'bk_biz_id': app_id,
                    'time_series_group_id': result.get('time_series_group_id'),
                })

                return info.get('bk_data_id'), info.get('access_token'), result.get('time_series_group_id')

            except Exception as err:
                logger.warning(f"该名称创建失败，失败原因:{err}")

        logger.error("远程创建监控平台data_id 失败，请联系管理员")
        return None, None, None

    def delete_monitor_data(self, app_id, time_series_group_id):
        """
            删除监控自定义指标配置
        """
        try:
            MonitorApi.delete_custom_time_series({
                'bk_username': self.bk_username,
                'bk_biz_id': app_id,
                'time_series_group_id': time_series_group_id,
            })

        except Exception as err:
            logger.error(f"删除监控配置失败，失败原因:{err}")

        finally:
            return True
