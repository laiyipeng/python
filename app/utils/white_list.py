# -*- coding: utf-8 -*-
from tm.sql import db

SUCCESS = 1

def checkWhiteList(app_id):
    sql = "select * from dev_whitelst where app_id='%s'" %(app_id)
    query = db.query(sql)
    if not query:
        sql = "insert into dev_whitelst (app_id) VALUES ('%s') returning id" %(app_id)
        id = db.insert(sql)
    else:
        id = query[0].get('id')
    return id

def whiteAppend(app_id, ad_id, type):
    ad_list = 'ad_lst' if type == '1' else 'black_ad_lst'
    sql = "select * from dev_whitelst where app_id='%s' and '%s'=ANY(%s)" % (app_id, ad_id, ad_list)
    query = db.query(sql)
    if not query:
        sql = "update dev_whitelst set %s = array_append(%s, '%s') where app_id='%s'" \
              % (ad_list, ad_list, ad_id, app_id)
        db.execute(sql)
        return 1
    return 0
