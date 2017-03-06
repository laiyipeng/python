# -*- coding: utf-8 -*-
from tm.sql import db
from app.utils.bit import setBit, clearBit, testBit


def filterWhiteName(list):
    if list:
        for item in list:
            list2 = []
            for item2 in item.get('ad_lst'):
                sql = "select title from advertisement where id='%s'" % (item2)
                query = db.query(sql)
                list2.append(query[0].get('title')) if query else ''
            item['ad_lst'] = zip(list2, item.get('ad_lst'))
    return list


charge_type_filter = {
    0: 'cpm',
    1: 'cpa',
    2: 'cpc',
    3: 'cps',
}

state_filter = {
    '0': '下线',
    '1': '上线',
}

carrier_filter = {
    '0': '无sim卡',
    '1': '移动',
    '2': '联通',
    '3': '电信',
}

ad_type_dict = {
    0: '广告条',
    1: '插屏',
    2: '开屏',
    3: '视频',
    4: '图标',
    5: '推送',
    6: '静默下载',
    7: '系统提示框',
    8: '不带取消系统提示框',
    9: '悬浮',
    10: '文件夹',
    11: '退出提示',
    888: '补报安装'
}

ad_display_type = {
    1: u'横幅',
    2: u'插屏',
    3: u'全屏',
    4: u'内嵌',
    5: u'信息流',
    6: u'富媒体',
    7: u'推送',
    8: u'打图标',
    9: u'系统提示框',
    10: u'PC内嵌',
    11: u'PC对联',
    12: u'PC对话框',
    13: u'图+',
    14: u'静默下载',
    15: u'悬浮',
    16: u'铺文件夹',
    17: u'退出框',
    888: u'补报安装'
}


def exemplar_filter(exemplar):
    exe = ''
    exemplar = int(exemplar)
    if exemplar == 0:
        exe += '下线'
    if testBit(exemplar, 0):
        exe += '横屏 '
    if testBit(exemplar, 1):
        exe += '插屏 '
    if testBit(exemplar, 2):
        exe += '开屏 '
    if testBit(exemplar, 3):
        exe += '视频 '
    if testBit(exemplar, 4):
        exe += '图标 '
    if testBit(exemplar, 5):
        exe += '推送 '
    if testBit(exemplar, 7):
        exe += '系统提示框 '
    if testBit(exemplar, 8):
        exe += '系统提示框2 '
    return exe


def dev_type_filter(dev_type):
    type = []
    dev_type = int(dev_type)
    if dev_type == 0:
        type.append('无')
    if testBit(dev_type, 0):
        type.append('通用类')
    if testBit(dev_type, 1):
        type.append('美女娱乐类')
    if testBit(dev_type, 2):
        type.append('应用工具类')
    if testBit(dev_type, 3):
        type.append('手机游戏类')
    return type


dev_type_dict = {
    0: '通用类',
    1: '美女娱乐类',
    2: '应用工具类',
    3: '手机游戏类',
}

bd_filter = {
    0: '求认领',
    4: '陈娟',
    7: '梦君',
    8: 'jojo',
    33: '黄甜',
    99: '龚玉芝',
    113: '啊龙',
    139: '鲁小青',
    155: '蝴蝶',
    7777: '公众号',
    8888: '公众号',
}

crm_filter = {
    45: '赖奕鹏',
    59: '李虹',
    60: '刘梦琪',
    62: '丹妮',
    66: '周玮',
    208: '戴霞',
    215: '飘飘',
    255: '金凤',
}

test_phone_imei = {
    '869804025618625': 'OPPO手机',
    '869334021610046': '蓝壳红米2',
    '865174026256211': '华为',
    '869070025788848': '小米（白色）',
    '869611020379669': '乐视手机',
    'A0000055F028C2': '华为 深灰色',
    '867066025660500': '华为（陈娟）',
    'DE60B664-C6E5-4C24-BFAC-3A2F2991D324': 'iphone6（丹妮）',
    '355446063375493': '傻逼甘斌',
    '867641020267079': '华为（嘿）',
    '358695073864378': '小帮',
    '867515020786579': '白壳小米',
    '861483030885095': '360',
}
