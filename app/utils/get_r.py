# -*- coding: utf-8 -*-
from flask import request

def get_r(req, args={}, method='GET'):
    r = request.args if method == 'GET' else request.form

    for k, v in args.items():
        if r.get(k):
            try:
                args[k] = args[k](r.get(k))
            except Exception, e:
                print('type error------------------------- '+str(e))
        else:
            args.pop(k)

    req.args = args
    return req

class r(object):

    def __init__(self, method='GET', args={}):
        self.method = method
        self.r = request.args if method == 'GET' else request.form
        self.args = args

    def confirm_r(self, required_args=[]):
        for item in required_args:
            if not self.r.get(item):
                return False
        return True

    def get_req(self, req):
        for k, v in self.args.items():
            if self.r.get(k):
                try:
                    self.args[k] = v(self.r.get(k))
                except Exception, e:
                    print('type error------------------------- '+str(e))
            else:
                self.args.pop(k)

        req.args = self.args
        return req