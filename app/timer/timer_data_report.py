#-*- coding: utf-8 -*-
import requests
import os
import datetime

host = 'http://admin.zmsdk.zonst.org/'
method_data_report = 'plugin/timer_data_report'
method_update_biz = 'update_biz'

class Timer(object):
    def __int__(self):
        pass

    def data_report(self):
        url = host + method_data_report
        try:
            res = requests.get(url)
            res = res.content
        except Exception, e:
            print(e)
            res = 'ERROR'
        return res

    def update_biz(self):
        url = host + method_update_biz
        try:
            res = requests.get(url)
            res = res.content
        except Exception, e:
            print(e)
            res = 'ERROR'
        return res

if __name__ == '__main__':
    timer = Timer()
    res_report = timer.data_report()
    res_biz = timer.update_biz()
    cmd = "echo " + str(datetime.datetime.now()) + "_" + res_report + "_" + res_biz + " >>/home/tonnn/cron/timer.log"
    os.system(cmd)