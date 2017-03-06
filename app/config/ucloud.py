# -*- coding: utf-8 -*-

from .base import BaseConfig

class UcloudConfig(BaseConfig):
    url = "http://10.0.0.7:8081/"
    url_source = "http://119.29.121.68:8088/"
    REDIS_URLS = {
        "default": "redis://119.29.12.229:6379"
    }
    DEBUG = False
    TESTING = False
