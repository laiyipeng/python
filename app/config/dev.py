# -*- coding: utf-8 -*-

from .base import BaseConfig

class DevConfig(BaseConfig):
    url_source = "http://10.0.10.3:1074/"
    url = "http://10.0.10.31:8080/"
    # url_zmns = "http://10.0.0.32:8080/"
    url_zmns = "http://119.29.112.123:8080/"
    REDIS_URLS = {
        "default": "redis://@localhost:6379/0"
    }
    ZMNS_API_HOST = 'http://119.29.112.123:8080/'