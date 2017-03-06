# -*- coding: utf-8 -*-

import logging
import urllib
import requests
import simplejson as json
from flask import current_app as app

from tm.util.sign import hexdigest_hash
from tm.util.password import hexdigest_password


class UserQuery(object):
    pass

class User(object):
    
    query = UserQuery()
    
    @classmethod
    def init_from_dict(cls, d):
        obj = cls()
        for key, value in d.iteritems():
            if hasattr(obj, key):
                raise
            setattr(obj, key, value)
        
        setattr(obj, "_raw_objects", d)
        return obj
    
    def is_authenticated(self):
        """是否验证用户?"""
        return True
        # return self.is_actived
        
    def is_active(self):
        """是否活动用户"""
        return True
        # return self.is_actived
        
    def is_anonymous(self):
        """是否匿名用户"""
        return False
        
    def get_id(self):
        return unicode(str(self.user_id))
        
    @staticmethod
    def _get_user_salt(login_name=None, t=None):
        """获取用户salt"""
        interface_url = app.config.get("RBAC_USER_SALT_URL", None)
        if interface_url is None:
            raise Exception("USER_SALT_URL is None")
        rbac_secret_key = app.config.get("RBAC_SECRET_KEY", None)
        if rbac_secret_key is None:
            raise Exception("RBAC_SECRET_KEY is None")
        
        sign = hexdigest_hash(secret_key=rbac_secret_key, login_name=login_name, t=t)
        request_args = dict(login_name=login_name, t=t, sign=sign)
        request_url = "%s?%s" % (interface_url, urllib.urlencode(request_args))
        r = requests.get(request_url)

        if r.status_code == 200:
            logging.debug("url=%s, r=%s" % (request_url, r.text))
            rr = json.loads(r.text)
            if rr['status'] == 200:
                return rr['salt']
        else:
            logging.error("url=%s, request bad" % request_url)
    
        return None
        
    @staticmethod
    def _get_user(login_name=None, login_password=None, t=None, salt=None):
        """获取用户信息"""
        interface_url = app.config.get("RBAC_USER_DATA_URL", None)
        if interface_url is None:
            raise Exception("RBAC_USER_DATA_URL is None")
        
        rbac_secret_key = app.config.get("RBAC_SECRET_KEY", None)
        if rbac_secret_key is None:
            raise Exception("RBAC_SECRET_KEY is None")
            
        site_id = app.config.get("RBAC_SITE_ID", None)
        if site_id is None:
            raise Exception("RBAC_SITE_ID is None")
        
        password = hexdigest_password("md5", salt, login_password)
        sign = hexdigest_hash(secret_key=rbac_secret_key, login_name=login_name, 
            login_password=password, t=t, site_id=site_id)
        request_args = dict(login_name=login_name, login_password=password, t=t,
            site_id=site_id, sign=sign)
        request_url = "%s?%s" % (interface_url, urllib.urlencode(request_args))
        r = requests.get(request_url)
        
        if r.status_code == 200:
            logging.debug("url=%s, r=%s" % (request_url, r.text))
            rr = json.loads(r.text)
            if rr['status'] == 200:
                return User.init_from_dict(rr['user'])
        else:
            logging.error("url=%s, request bad" % request_url)
        return None
