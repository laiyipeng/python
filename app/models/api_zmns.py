# -*- coding: utf-8 -*-
from flask import current_app

import requests


class ZMNS_API():
    def __init__(self):
        pass

    @classmethod
    def get(cls, uri, args=''):
        host = current_app.config['ZMNS_API_HOST'] + uri + args
        res = requests.get(host)
        res = res.content
        return res

    @classmethod
    def post(cls, uri, args=''):
        host = current_app.config['ZMNS_API_HOST'] + uri
        res = requests.post(host, data=args)
        res = res.content
        return res

    # 计划
    @classmethod
    def plan_list(cls, args=''):
        uri = 'plan/list'
        return cls.get(uri, args)

    # 广告主
    @classmethod
    def cp_list(cls, args=''):
        uri = 'cp/list'
        return cls.get(uri, args)

    @classmethod
    def add_cp(cls, args=''):
        uri = 'cp/add'
        return cls.post(uri, args)

    # 产品
    @classmethod
    def product_list(cls, args=''):
        uri = 'product/list'
        return cls.get(uri, args)

    @classmethod
    def edit_product(cls, args=''):
        uri = 'product/edit'
        return cls.post(uri, args)

    @classmethod
    def add_product(cls, args=''):
        uri = 'product/add'
        return cls.post(uri, args)

    # 财务
    @classmethod
    def finance_list(cls, args=''):
        uri = 'cp/finance/list'
        return cls.get(uri, args)

    @classmethod
    def edit_finance(cls, args=''):
        uri = 'cp/finance/edit'
        return cls.post(uri, args)

    @classmethod
    def add_finance(cls, args=''):
        uri = 'cp/finance/add'
        return cls.post(uri, args)

    # 发票
    @classmethod
    def add_invoice(cls, args=''):
        uri = 'cp/invoice/add'
        return cls.post(uri, args)

    @classmethod
    def invoice_list(cls, args=''):
        uri = 'cp/invoice/list'
        return cls.get(uri, args)

    # 邮寄
    @classmethod
    def deliver_list(cls, args=''):
        uri = 'cp/deliver/list'
        return cls.get(uri, args)

    @classmethod
    def add_deliver(cls, args=''):
        uri = 'cp/deliver/add'
        return cls.post(uri, args)

    # 支付信息
    @classmethod
    def payinfo_list(cls, args=''):
        uri = 'cp/payinfo/list'
        return cls.get(uri, args)

    @classmethod
    def add_payinfo(cls, args=''):
        uri = 'cp/payinfo/add'
        return cls.post(uri, args)

    # 充值
    @classmethod
    def charge_list(cls, args=''):
        uri = 'cp/recharge/list'
        return cls.get(uri, args)

    @classmethod
    def add_charge(cls, args=''):
        uri = 'cp/recharge/add'
        return cls.post(uri, args)

    # 收益
    @classmethod
    def earnings_list(cls, args=''):
        uri = 'adm/earnings/list'
        return cls.get(uri, args)
