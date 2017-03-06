# -*- coding: utf-8 -*-

import urllib
import urlparse

import simplejson as json
import requests

from ..utils import encoded_dict
from flask import flash


class BaseQuery(object):
    @classmethod
    def _fix_kwargs(cls, kwargs):
        return dict([(k, v) for k, v
                     in kwargs.iteritems() if v is not None])

    @classmethod
    def response(cls, host, uri, kwargs={}, method="get",
                 content_type="str", files={}):
        kwargs = cls._fix_kwargs(kwargs)
        default = {"error_no": 0, "error_msg": "", "data": []}
        url = urlparse.urljoin(host, uri)
        res = getattr(requests, method)
        get_args = "" if method == "post" else urllib.urlencode(encoded_dict(kwargs))
        post_args = kwargs if method == "post" or method == 'put' else {}
        post_data_type = "json" if content_type == "json" else "data"
        print(url)
        if method == "get":
            url = "?".join([
                url,
                urllib.urlencode(encoded_dict(kwargs))
            ])
        response = res(url, **{
            post_data_type: post_args,
            "files": files
        })

        print '请求地址: %s' % url
        print 'post参数: %s ' % post_args

        if response.status_code != 200:
            flash(u"远程服务器错误", category="danger")
            return default if kwargs.get('num') else default["data"]
        response_obj = json.loads(response.content)
        if response_obj['error_no'] != 0:
            # flash(response_obj["error_msg"], category="danger")
            default.update(response_obj)
            return default if kwargs.get('num') else default["data"]
        default.update(response_obj)
        return default if kwargs.get('num') else default["data"]

