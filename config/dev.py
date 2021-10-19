# -*- coding: utf-8 -*-
import importlib

from config import RUN_VER

if RUN_VER == 'open':
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # noqa

# 本地开发环境
RUN_MODE = 'DEVELOP'

# APP本地静态资源目录
STATIC_URL = '/static/'

# APP静态资源目录url
# REMOTE_STATIC_URL = '%sremote/' % STATIC_URL


BK_STATIC_URL = STATIC_URL + 'assets'

# 加载各个版本特殊配置
try:
    conf_module = "adapter.sites.{run_ver}.config.dev".format(run_ver=RUN_VER)
    _module = importlib.import_module(conf_module)
    for _setting in dir(_module):
        if _setting == _setting.upper():
            locals()[_setting] = getattr(_module, _setting)
except ImportError:
    pass

# 如果不确定需要追加的具体域名, 可以先配置以下的正则白名单, 但在生产环境下建议准确配置相关的域名,解决本地跨域问题
CORS_ORIGIN_REGEX_WHITELIST = [
    # 是线上环境中, 开了了独立子域名(新应用默认开启)的应用访问域名后缀
    r"http://.*",
    # 旧版应用使用子路径访问
]
CORS_ALLOW_CREDENTIALS = True

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    from config.local_settings import *  # noqa
except ImportError:
    pass
