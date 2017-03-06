#-*- coding: utf-8 -*-
import requests
import os
import datetime

host = 'http://admin.zmsdk.zonst.org/'
method_report_image = 'report_image'

class Timer(object):
    def __int__(self):
        pass

    def report_image(self):
        url = host + method_report_image
        try:
            res = requests.get(url)
            res = res.content
        except Exception, e:
            print(e)
            res = 'ERROR'
        return res

if __name__ == '__main__':
    timer = Timer()
    res_report = timer.report_image()
    cmd = "echo " + str(datetime.datetime.now()) + "_" + res_report + " >>/home/tonnn/cron/timer.log"
    os.system(cmd)