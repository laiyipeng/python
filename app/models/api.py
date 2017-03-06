# -*- coding: utf-8 -*-

import logging
import urllib
import urllib2
import json
import sys, datetime
import requests

# sdk
method_crm_dataAdd = 'crm/DataAdd'
method_bdm_DataReport = 'bdm/DataReport'
method_AdList = 'bdm/AdList'

# 素材
method_GetTypes = 'GetTypes'
method_GetDimensions = 'GetDimensions'
method_GetMaterials = 'GetMaterials'
method_GetImages = 'GetImages'
method_Binding = 'Binding'
method_reportData = 'reportData'

# 统一广告
method_zmnsbdm_DataReport = 'zmnsbdm/DataReport'


class API():
    def __init__(self, url):
        self.url = url

    def api_get(self, method, args):
        tmp_url = self.url + method + args
        req = urllib2.Request(tmp_url)
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        return res

    def api_post(self, method, args):
        tmp_url = self.url + method
        req = urllib2.Request(tmp_url, args, {'Content-Type': 'application/json'})
        res_data = urllib2.urlopen(req)
        res = res_data.read()
        return res


# 初始化
def DBServerInit(url, url_source, url_zmns):
    global g_url, g_url_source, g_url_zmns
    g_url = url
    g_url_source = url_source
    g_url_zmns = url_zmns


def ApiGet(url, method, args=''):
    tmp_url = url + method + str(args)
    req = urllib2.Request(tmp_url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res


def ApiPost(url, method, args=''):
    tmp_url = url + method
    req = urllib2.Request(tmp_url, args, {'Content-Type': 'application/json'})
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    return res


# 素材api

# 绑定素材广告
def Binding(args):
    res = ApiPost(g_url_source, method_Binding, args)
    return res


def GetTypes(args):
    res = ApiGet(g_url_source, method_GetTypes, args)
    return res


def GetDimensions():
    res = ApiGet(g_url_source, method_GetDimensions)
    return res


def GetMaterials(args):
    res = ApiGet(g_url_source, method_GetMaterials, args)
    return res


def GetImages(args):
    res = ApiGet(g_url_source, method_GetImages, args)
    return res


def reportData(args):
    res = ApiPost(g_url_source, method_reportData, args)
    return res


# ----------------------------------
# sdk api
# ----------------------------------

# 导入数据到crm后台
def PushToCrm(args):
    res = ApiPost(g_url, method_crm_dataAdd, args)
    return res


# 导入数据到bdm后台
def PushToBdm(args):
    res = ApiPost(g_url, method_bdm_DataReport, args)
    return res


def AdList(args):
    res = ApiGet(g_url, method_AdList, args)
    return res


# 统一广告--------------------------------------------------------
def zmnsbdm_DataReport(args):
    res = ApiPost(g_url_zmns, method_zmnsbdm_DataReport, args)
    return res


# 广告
def productList(args=''):
    res = ApiGet(g_url_zmns, 'product/list', args)
    res = json.loads(res)
    return res


# 计划
def planList(args=''):
    res = ApiGet(g_url_zmns, 'plan/list', args)
    res = json.loads(res)
    return res
