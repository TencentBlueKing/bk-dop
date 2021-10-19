# -*- coding: utf-8 -*-
import os

# sdk
ESB_SDK_NAME = "adapter.sites.open.blueking.component"

# bk_login
OAUTH_COOKIES_PARAMS = {"bk_token": "bk_token"}
RUN_VER_DISPLAY = os.environ.get("RUN_VER_DISPLAY", "企业版")
INIT_SUPERUSER = ["admin"]

BIZ_ACCESS_URL = os.getenv("BKAPP_BIZ_ACCESS_URL", "")
DEMO_BIZ_ID = os.getenv("BKAPP_DEMO_BIZ_ID", "")
DEMO_BIZ_EDIT_ENABLED = bool(os.getenv("BKAPP_DEMO_BIZ_EDIT_ENABLED", ""))


