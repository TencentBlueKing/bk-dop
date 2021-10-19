# -*- coding: utf-8 -*-
from blueapps.conf.log import get_logging_config_dict
from blueapps.conf.default_settings import *  # noqa

# 这里是默认的 INSTALLED_APPS，大部分情况下，不需要改动
# 如果你已经了解每个默认 APP 的作用，确实需要去掉某些 APP，请去掉下面的注释，然后修改
# INSTALLED_APPS = (
#     'bkoauth',
#     # 框架自定义命令
#     'blueapps.contrib.bk_commands',
#     'django.contrib.admin',
#     'django.contrib.auth',
#     'django.contrib.contenttypes',
#     'django.contrib.sessions',
#     'django.contrib.sites',
#     'django.contrib.messages',
#     'django.contrib.staticfiles',
#     # account app
#     'blueapps.account',
# )

# 请在这里加入你的自定义 APP
INSTALLED_APPS += (
    'apps.hadoop',
    'apps.es',
    'apps.kafka',
    'pipeline',
    'pipeline.engine',
    'pipeline.component_framework',
    'pipeline.eri',
    'pipeline.django_signal_valve',
    'django_celery_beat',
    'django_celery_results',
    'rest_framework',
    'django_filters',
    'corsheaders',
    'atoms.es_bamboo',
    'atoms.kafka_bamboo',
    'atoms.hadoop_bamboo',
    'atoms.monitor_bamboo',
    'apps.globalview',
    'django_apscheduler',
)

# 这里是默认的中间件，大部分情况下，不需要改动
# 如果你已经了解每个默认 MIDDLEWARE 的作用，确实需要去掉某些 MIDDLEWARE，或者改动先后顺序，请去掉下面的注释，然后修改
# MIDDLEWARE = (
#     # request instance provider
#     'blueapps.middleware.request_provider.RequestProvider',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.auth.middleware.AuthenticationMiddleware',
#     'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     # 跨域检测中间件， 默认关闭
#     # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'django.middleware.security.SecurityMiddleware',
#     # 蓝鲸静态资源服务
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     # Auth middleware
#     'blueapps.account.middlewares.WeixinLoginRequiredMiddleware',
#     'blueapps.account.middlewares.LoginRequiredMiddleware',
#     # exception middleware
#     'blueapps.core.exceptions.middleware.AppExceptionMiddleware'
# )

# 自定义中间件
MIDDLEWARE = (
    # CorsMiddleware 尽量放在靠前的位置
    # 特别是在任何可以生成响应的中间件之前，例如Django的CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'blueapps.middleware.bkui.middlewares.BkuiPageMiddleware',
) + MIDDLEWARE

CORS_ALLOW_CREDENTIALS = True

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'INFO'

#
# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v={{ STATIC_VERSION }}"></script>
# mako 模板中：<script src="/a.js?v=${ STATIC_VERSION }"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
#
STATIC_VERSION = '1.0'

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
IS_USE_CELERY = True

# CELERY 并发数，默认为 2，可以通过环境变量或者 Procfile 设置
CELERYD_CONCURRENCY = os.getenv('BK_CELERYD_CONCURRENCY', 2)

# CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
CELERY_IMPORTS = ()

# load logging settings
LOGGING = get_logging_config_dict(locals())

# 初始化管理员列表，列表中的人员将拥有预发布环境和正式环境的管理员权限
# 注意：请在首次提测和上线前修改，之后的修改将不会生效

# 使用mako模板时，默认打开的过滤器：h(过滤html)
MAKO_DEFAULT_FILTERS = ['h']

# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 是否需要对AJAX弹窗登录强行打开
IS_AJAX_PLAIN_MODE = False


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (os.path.join(BASE_DIR, "static/assets"), os.path.join(BASE_DIR, "templates"),),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # "blueapps.template.context_processors.blue_settings",
                "common.django.context_processors.blue_settings",
            ],
        },
    },
    {
        "BACKEND": "blueapps.template.backends.mako.MakoTemplates",
        "DIRS": (os.path.join(BASE_DIR, MAKO_DIR_NAME),),
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "blueapps.template.context_processors.blue_settings",
            ],
            # mako templates cache, None means not using cache
            "module_directory": os.path.join(
                os.path.dirname(BASE_DIR), "templates_module", APP_CODE
            ),
        },
    },
]

# 国际化配置
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

TIME_ZONE = 'Asia/Shanghai'
LANGUAGE_CODE = 'zh-hans'
DATAAPI_TIME_ZONE = "Etc/GMT-8"
USE_TZ = True

LANGUAGES = (
    ('en', u'English'),
    ('zh-hans', u'简体中文'),
)

"""
以下为框架代码 请勿修改
"""
# celery settings
# if IS_USE_CELERY:
#     INSTALLED_APPS = locals().get('INSTALLED_APPS', [])
#     import djcelery
#
#     INSTALLED_APPS += ('djcelery',)
#     djcelery.setup_loader()
#     CELERY_ENABLE_UTC = False
#     CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"

# remove disabled apps
if locals().get('DISABLED_APPS'):
    INSTALLED_APPS = locals().get('INSTALLED_APPS', [])
    DISABLED_APPS = locals().get('DISABLED_APPS', [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]

    _keys = (
        'AUTHENTICATION_BACKENDS',
        'DATABASE_ROUTERS',
        'FILE_UPLOAD_HANDLERS',
        'MIDDLEWARE',
        'PASSWORD_HASHERS',
        'TEMPLATE_LOADERS',
        'STATICFILES_FINDERS',
        'TEMPLATE_CONTEXT_PROCESSORS',
    )

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        if locals().get(_key) is None:
            continue
        locals()[_key] = tuple([_item for _item in locals()[_key] if not _item.startswith(_app + '.')])

# 调整默认使用api上云版访问
BK_API_USE_BKCLOUDS_FIRST = True

# REST_FRAMEWORK 全局设定
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
}

# ===============================================================================
# FeatureToggle 特性开关：以内部版为准，其它版本根据需求调整
# ===============================================================================
FEATURE_TOGGLE = {
    # 是否使用数据平台token鉴权
    "bkdata_token_auth": os.environ.get("BKAPP_BKDATA_TOKEN_AUTH", "off"),
}

SENSITIVE_PARAMS = ['app_code', 'app_secret', 'bk_app_code', 'bk_app_secret']

