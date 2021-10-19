# -*- coding: utf-8 -*-
import importlib

from config import RUN_VER
if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 正式环境
RUN_MODE = 'PRODUCT'

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = 'ERROR'

# V2
# import logging
# logging.getLogger('root').setLevel('INFO')
# V3
# import logging
# logging.getLogger('app').setLevel('INFO')


# 正式环境数据库可以在这里配置
# 默认 default 请不要修改，如果使用了外部数据库，请联系【蓝鲸助手】授权
# DATABASES.update(
#     {
#         # 外部数据库授权，请联系 【蓝鲸助手】
#         'external_db': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': '',  # 外部数据库名
#             'USER': '',  # 外部数据库用户
#             'PASSWORD': '',  # 外部数据库密码
#             'HOST': '',  # 外部数据库主机
#             'PORT': '',  # 外部数据库端口
#         },
#     }
# )

# Fixed celery beat hang
USE_TZ = True

BK_STATIC_URL = STATIC_URL + 'assets'

# 加载各个版本特殊配置
try:
    conf_module = "adapter.sites.{run_ver}.config.prod".format(run_ver=RUN_VER)
    _module = importlib.import_module(conf_module)
    for _setting in dir(_module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(_module, _setting)
except ImportError:
    pass
