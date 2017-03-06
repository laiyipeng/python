# -*- coding: utf-8 -*-
import datetime


def StrToDate(date, day=0):
    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    date += datetime.timedelta(days=day)
    return date
