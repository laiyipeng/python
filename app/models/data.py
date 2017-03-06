# -*- coding: utf-8 -*-

from flask import current_app
import urllib2
import json

from . import BaseQuery


class Data(BaseQuery):
    @classmethod
    def query(cls, **kwargs):
        host = current_app.config['API_HOST']
        uri = "Data"
        return cls.response(host, uri, kwargs)

    @classmethod
    def data_report(cls, **kwargs):
        host = current_app.config['API_HOST']
        uri = "DataReport"
        results = cls.response(host, uri, kwargs, method='post', content_type='json')
        return results

    @classmethod
    def data_push(cls, **kwargs):
        host = current_app.config['API_HOST']
        uri = "data_push"
        results = cls.response(host, uri, kwargs, method='post', content_type='json')
        return results

    @classmethod
    def del_commission(cls, order_date, product_id):
        return {'status': 200}

    @classmethod
    def dataverify_list(cls, **kwargs):
        host = current_app.config['API_HOST']
        uri = "dataverify_list"
        results = cls.response(host, uri, kwargs)
        return results

    @classmethod
    def data_allot_list(cls, **kwargs):
        host = current_app.config['API_HOST']
        uri = "data_allot_list"
        results = cls.response(host, uri, kwargs)
        return results

    @classmethod
    def data_zm(cls, **kwargs):
        host = current_app.config['ZM_API_HOST']
        uri = "bdm_commission/data_report"
        return cls.response(host, uri, kwargs)