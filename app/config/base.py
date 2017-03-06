# -*- coding: utf-8 -*-

class BaseConfig(object):
    
    DEBUG = True
    
    # Bootstrap
    BOOTSTRAP_SERVE_LOCAL = True
    
    # 应用私钥
    SECRET_KEY = 't(5hxsl0t*(^7v9dftc)k47cp0*miuic=4kw^1bm(iey#*z2-h'
    
    # Postgrsql数据库配置
    DATABASE_URLS = {
        # 'default': 'postgresql://pgsql:123456@10.0.10.2:5432/zmfastplugin',
        # 'default': 'postgresql://zmadsdk:zmfastpluginnew@119.29.12.229:5432/zmfastplugin',
        'default': 'postgresql://zmadsdk:zmfastpluginnew@10.0.0.3:5432/zmfastplugin',
    }
    
    # Redis数据库配置
    # REDIS_URLS = {
    #     "default": "redis://10.0.0.3:6379"
    # }
    
    # Session以及Cookie配置
    # DEFAULT_DOMAIN = 'http://www.zonst.com/'
    COOKIE_DOMAIN = ".zonst.org"
    COOKIE_MAX_AGE = 24*60*60

    SESSION_COOKIE_NAME = 'zmplugin'
    

    # 统一账号接口
    RBAC_SITE_ID = 14
    RBAC_SECRET_KEY = "d93d3fef-c354-4ed4-b781-b6402ff1bc03"

    RBAC_USER_SALT_URL = 'http://119.29.136.230:8080/auth/salt'
    RBAC_USER_DATA_URL = "http://119.29.136.230:8080/auth/login"

    ENABLE_LOGIN_CAPTCHA = False
    PERMANET_SESSION_LIFETIME = 60*60*24
    # 短信验证
    # ENABLE_MSG_VERIFY = True
    # RBAC_USER_VERIFY_URL = 'http://rbac.api.xq5.com/auth/msg_verify'