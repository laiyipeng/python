# -*- coding: utf-8 -*-
from flask import request

# 拼凑参数
def setArgs(dict, args=''):
    for k, v in dict.items():
        args += ('&%s=' %(k) + str(v)) if v else ''
    return args

# 拼凑url args
def _setArgs(dict):
    args = ''
    for k, v in dict.items():
        if args:
            args += ('&%s=' %(k) + str(v)) if v else ''
        else:
            args += ('?%s=' %(k) + str(v)) if v else ''
    return args

#拼凑sql语句
def setSQL(sql, args={}):
    for k, v in args.items():
        if v:
            if 'where' in sql:
                sql += " and %s='%s'" % (k, v)
            else:
                sql += " where %s='%s'" % (k, v)
    return sql

# 获取接收参数，并以dict的形式返回
def receive_args(args={}, m='GET'):
    _args = {}
    method = request.args if m == 'GET' else request.form
    for k, v in args.items():
        _args.update({k: method.get(k).replace(' ', '') if method.get(k) else v})
    return _args