# -*- coding: utf-8 -*-

def set_image_lst(*args):
    ret = ''
    for item in args:
        if item:
            if 'http' in ret:
                ret += ',' + item
            else:
                ret += item
    return ret