# -*- coding: utf-8 -*-

import os
import logging
from flask.ext.script import Manager
from flask.ext.script import Shell
from app import create_app


def task():
    print "task ..."

# 配置日志
logging.basicConfig(level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')

config_name = os.getenv('TEST_config_name') or "dev"
app = create_app(config_name)
manager = Manager(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug = True, threaded = True, port = 5500)
