# -*- coding: utf-8 -*-

from decimal import Decimal


def encoded_dict(in_dict):
    out_dict = {}
    if in_dict:
        for k, v in in_dict.iteritems():
            if isinstance(v, unicode):
                v = v.encode('utf8')
            elif isinstance(v, Decimal):
                v = str(v)
            out_dict[k] = v
    return out_dict