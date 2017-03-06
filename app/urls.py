# -*- coding: utf-8 -*-


from controllers2.crontab import crontab
from controllers2.ad import ad_plugin

routers = (
    (ad_plugin, ''),
    (crontab, ''),
)
