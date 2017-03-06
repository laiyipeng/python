# -*- coding: utf-8 -*-

import requests
import time

from flask import Blueprint, g, jsonify, request
from tm.sql import db
from ..models.api import *
from ..utils.args import setArgs

reload(sys)
sys.setdefaultencoding('utf8')

crontab = Blueprint("crontab", __name__)

@crontab.route('/plugin/data_report_zmns')
def data_report_zmns():
    sql = '''select coalesce(sum(install),0) as install, coalesce(sum(show),0) as show, coalesce(sum(click),0) as click, coalesce(sum(download),0) as download,
            coalesce(sum(close),0) as close, coalesce(sum(active),0) as active,
            ad_type as exemplar, ad_id, cast(time as varchar(10)) as time
            from daily_data_ns
            where time>='%s' and time<='%s'
            group by ad_id, time, ad_type''' % (g.before, g.now)
    query = db.query(sql)

    def func(x):
        x['plan_id'] = 1
        x['channel'] = 56545
        return x
    query = map(func, query)
    data = {
        'lst': query,
        'pt_type': 2
    }
    res = zmnsbdm_DataReport(json.dumps(data))
    return 'data_report_zmns-----------' + res

@crontab.route('/plugin/timer_data_report')
def timer_data_report():
    # id in (97, 135, 142, 141, 148) or w_id in (2150, 2181, 2183, 2190, 2274, 2277, 2325)
    sql = '''select * from
            (select (case when coalesce(sum(b.install),0) > coalesce(sum(a.active),0) then coalesce(sum(a.install),0) else coalesce(sum(a.active),0) end) as cp_norder, coalesce(sum(a.show),0) as track, coalesce(sum(a.click),0) as clk, a.ad_id, cast(time as varchar(10)) as report_date
            from daily_data_ns as a, daily_data_detail as b
             where time>='%s' and time<='%s' and b.dailydata_id=a.id
            group by ad_id, time ) A,
            (select id, w_id as product_id from advertisement where auto_install=1) B
            where A.ad_id = B.id''' % (g.before, g.now)
    query = db.query(sql)

    data = {
        'lst': query,
        'member_id': 56545
    }
    res = PushToBdm(json.dumps(data))

    warning_id = json.loads(res).get('warning_id')
    if warning_id:
        for item in warning_id:
            sql = "update advertisement set state=0 where id=%s" % (item)
            db.execute(sql)

    return 'data_report-----------' + res


@crontab.route('/plugin/timer_data_report_bf')
def timer_data_report_bf():
    sql = '''select * from
            (select coalesce(sum(install),0) as cp_norder, coalesce(sum(show),0) as track, coalesce(sum(click),0) as clk, ad_id, cast(time as varchar(10)) as report_date
            from daily_data_ns
             where time<='%s' and time>='2016-03-27'
            group by ad_id, time ) A,
            (select id, w_id as product_id from advertisement where id in (383)) B
            where A.ad_id = B.id''' % (g.now)
    query = db.query(sql)

    data = {
        'lst': query,
        'member_id': 56545
    }
    res = PushToBdm(json.dumps(data))

    warning_id = json.loads(res).get('warning_id')
    if warning_id:
        for item in warning_id:
            sql = "update advertisement set state=0 where id=%s" % (item)
            db.execute(sql)

    return 'data_report-----------' + res


@crontab.route('/update_ad_result', methods=['GET', 'POST'])
def update_ad_result():
    sdate = request.form.get('sdate')
    edate = request.form.get('edate')

    sql = '''select A.*, B.all_pay, C.all_install, D.all_active_new from
            (select a.ad_id, sum(a.show) as show, sum(a.click)click, sum(a.download)download, sum(a.install)install, a.time,
            b.w_id, c.earnings_install as earning, c.back_num
            from daily_data_ns as a, advertisement as b, ad_clearing as c
            where a.ad_id=b.id and c.ad_id=b.id and c.time=a.time and a.time>='%s' and a.time<='%s'
            group by a.ad_id, a.time, c.earnings_install, c.back_num, b.w_id)A,

            (select sum(earnings_pre)all_pay, time as time1
            from dev_clearing
            where time>='%s' and time<='%s'
            group by time1)B,

            (select sum(install)all_install, time as time2
            from daily_data_ns
            where time>='%s' and time<='%s'
            group by time2)C,

            (select sum(active_new)all_active_new, time as time3
            from plgin_data
            group by time3)D
            where A.time=B.time1 and B.time1=C.time2 and C.time2=D.time3'''\
          % (sdate, edate, sdate, edate, sdate, edate)
    list = db.query(sql)

    for item in list:
        item.update({
            'pay': (float(item.all_pay) * item.install / item.all_install + float(item.earning) * 0.065) if item.all_install else 0,
        })
        item.update({
            'profit': float(item.earning) - item.pay,
            'ecpm': (item.earning / item.show * 1000) if item.show else 0,
            'arpu': (item.earning / item.install) if item.install else 0,
            'active_arpu': (item.earning / item.all_active_new) if item.all_active_new else 0,
        })


        sql = "select id from ad_result where ad_id=%s and date='%s'" %(item.ad_id, item.time)
        id = db.query(sql)

        if id:
            sql = '''update ad_result set show=%s, click=%s, download=%s, install=%s, all_active_new=%s, back_num=%s,
                    earning=%s, pay=%s, ecpm=%s, arpu=%s, active_arpu=%s where id=%s''' \
                  %(item.show, item.click, item.download, item.install, item.all_active_new, item.back_num, item.earning, item.pay,
                    item.ecpm, item.arpu, item.active_arpu, id[0].get('id'))
        else:
            sql = '''insert into ad_result
                    (ad_id, show, click, download, install, all_active_new, back_num, earning, pay, ecpm, arpu, active_arpu, date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s')'''\
                  % (item.ad_id, item.show, item.click, item.download, item.install, item.all_active_new, item.back_num, item.earning, item.pay, item.ecpm, item.arpu, item.active_arpu, item.time)
        db.execute(sql)
    return json.dumps({'status': 200})

# 更新分发商务，分发名
@crontab.route('/update_biz')
def update_biz():
    sql = "select w_id from advertisement where w_id!=0 and w_title=''"
    query = db.query(sql)

    from tm.util.sign import hexdigest_hash
    SECRET_KEY = "9157cab7-645f-4b35-8fa5-d5c9975defce"
    api_host = "http://api.wauee.com"

    for item in query:
        request_args = {
                "pid": item.get('w_id'),
                "page": 1,
                "per_page": 10000,
                "secret_key": SECRET_KEY,
                "t": int(time.time()),
                "fields": 'biz,ad_price,name',
        }
        oauth_key = hexdigest_hash(pop_keys=["oauth_key"], **request_args)
        request_args.update({"oauth_key": oauth_key})
        request_args.pop("secret_key")
        uri = "products"
        request_url = "?".join(("/".join((api_host, uri)), urllib.urlencode(request_args)))
        res = requests.get(request_url)
        res = res.content
        data = json.loads(res).get('data')
        bd_id = data[0].get('biz') if data else 0
        ad_price = data[0].get('ad_price') if data else 0
        name = data[0].get('name') if data else ''

        sql = "update advertisement set bd_id=%s, adv_price=%s, w_title='%s' where w_id=%s" \
              % (bd_id if bd_id else 0, ad_price if ad_price else 0, name, item.get('w_id'))
        db.execute(sql)
    return json.dumps({'status': 200})


# 上报图片数据
@crontab.route('/report_image')
def report_image():
    sql = '''select ad_id, image as image_url, count(case when show=1 then 1 end) as show, count(case when click=1 then 1 end) as click, cast(time as varchar(20)) as date
                from realtime_data
                where time='%s' and image != ''
                group by ad_id, image, time
                ''' % (str(g.before))
    query = db.query(sql)

    args_dict = {
        'platform_id': 1,
        'lst': query,
    }
    res = reportData(json.dumps(args_dict))
    return 'report_image-----------' + res