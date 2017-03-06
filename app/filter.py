# -*- coding: utf-8 -*-
from .utils.filter import *


def configure_template_filters(app):
    @app.template_filter()
    def ad_type_filter(ad_type):
        return ad_type_dict.get(ad_type)

    @app.template_filter()
    def dev_type_filter(dev_type):
        return dev_type_dict.get(dev_type)

    @app.template_filter()
    def ad_display_type_name(ad_type):
        return ad_display_type.get(ad_type, u'未知')
