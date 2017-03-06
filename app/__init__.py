# -*- coding: utf-8 -*-

import importlib
import logging
import simplejson as json
import datetime

from flask import Flask, g
from flask.ext.login import current_user, AnonymousUserMixin, LoginManager

from tm.rbac import Rbac
#import rbac.acl
#import bootstrap
from tm.rbac import Rbac
from tm.bootstrap import Bootstrap
from tm.sql import DatabaseWrapper
from tm.redis import RedisWrapper
from .models.api import DBServerInit
from filter import configure_template_filters
# import timer.timer_data_report as LocalTimer


def load_config_class(config_name):
    """导入config配置"""
    
    config_class_name = "%sConfig" % config_name.capitalize()
    
    app_name = __name__
    mod = importlib.import_module('%s.config.%s' % (app_name, config_name))
    config_class = getattr(mod, config_class_name, None)
    return config_class

def create_app(config_name):
    """创建app"""
    app = Flask(__name__)
    
    config_class = load_config_class(config_name)
    app.config.from_object(config_class)

    Bootstrap(app)
    DatabaseWrapper.init_app(app)
    RedisWrapper.init_app(app)
    configure_blueprint(app)
    Rbac(app)
    DBServerInit(config_class.url, config_class.url_source, config_class.url_zmns)
    configure_template_filters(app)
    # LocalTimer.timer_init()

    configure_context_processors(app)
    return app

def configure_blueprint(app):
    """注册初始化blueprint"""
    from .urls import routers
    
    for blueprint, url_prefix in routers:
        app.register_blueprint(blueprint, url_prefix=url_prefix)

def configure_context_processors(app):
    """配置上下文"""
    @app.before_request
    def before_request():
        g.now = datetime.datetime.now().date()
        g.before = g.now - datetime.timedelta(days=1)
        g.num = 50
