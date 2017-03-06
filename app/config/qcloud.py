# -*- coding: utf-8 -*-

from .base import BaseConfig

class QcloudConfig(BaseConfig):
    
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_DOMAIN = ".zonst.org"

    url = 'http://10.0.0.7:8081/'
    url_source = "http://10.0.0.7:8088/"
    REDIS_URLS = {
        "default": "redis://:crs-olktyvs7:a123456789@10.0.0.11:6379/"
    }
    url_zmns = "http://10.0.0.32:8080/"
    ZMNS_API_HOST = 'http://10.0.0.32:8080/'
