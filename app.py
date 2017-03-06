# -*- coding: utf-8 -*-

import os
from app import create_app

config_name = os.getenv('TEST_config_name') or "dev"
app = create_app(config_name)
