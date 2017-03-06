# -*- coding: utf-8 -*-

import os
import logging
from app import create_app

# 配置日志
logging.basicConfig(level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')

config_name = os.getenv('PLUGIN_DEV_NAME') or "dev"
app = create_app(config_name)