# -*- coding: utf-8 -*-

import requests
import uuid
import json
import redis
from datetime import datetime, timedelta
from itertools import groupby

from flask import Blueprint, g, jsonify
from flask import redirect, url_for, request, flash
from flask import render_template
from flask.ext.login import login_required, current_user

from app.utils import pagination
from ..models.api import *
from ..utils.args import setArgs, _setArgs, setSQL, receive_args
from ..utils.date import StrToDate
from ..utils.pagination import *
from ..utils.report_image import set_image_lst
from ..models.api_zmns import ZMNS_API as adm

reload(sys)
sys.setdefaultencoding('utf8')

UPLOAD_FOLDER = 'app/'
UPLOAD_FOLDER_JAR = '/static/jar'
UPLOAD_FOLDER_CP = 'static/upload/cp'
UPLOAD_FOLDER_KP = 'static/upload/kp'
UPLOAD_FOLDER_BN = 'static/upload/bn'
UPLOAD_FOLDER_MD = 'static/upload/md'
UPLOAD_FOLDER_TB = 'static/upload/tb'
UPLOAD_FOLDER_TS = 'static/upload/ts'

ALLOWED_FILES = ['apk', 'jar', 'rar']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_FILES


ad_plugin = Blueprint("ad_plugin", __name__)

pool = redis.ConnectionPool.from_url('redis://:crs-cqvbqrtb:zonst1234@10.0.0.74:6379')
# pool = redis.ConnectionPool.from_url('redis://10.0.10.2:19200/0')
red = redis.Redis(connection_pool=pool)


@ad_plugin.route('/plugin/ad_add', methods=['GET', 'POST'])
@login_required
def ad_add():
    if request.method == "POST":
        productname = request.form.get('productname') or ''
        title_acronym = request.form.get('title_acronym') or ''
        w_id = request.form.get('w_id') or '0'
        packname = request.form.get('packname') or ''
        target_type = request.form.get('target_type') or '2'
        target = request.form.get('target').replace('cdn1.zm.', 'cdn1.sdk.') or ''
        target_logo = request.form.get('target_logo') or ''
        contant_installed = request.form.get('contant_installed') or ''
        contant = request.form.get('contant') or ''
        auto_download = request.form.get('auto_download') or 0
        state = request.form.get('state') or 0
        type_all = request.form.getlist('dev_type')
        dev_type = 0
        for item in type_all:
            dev_type += int(item)
        exemplar_all = request.form.getlist('exemplar')
        exemplar = int(0)
        for item in exemplar_all:
            exemplar = exemplar + int(item)

        # 判断展现种类
        bn = testBit(exemplar, 0)
        cp = testBit(exemplar, 1)
        kp = testBit(exemplar, 2)
        md = testBit(exemplar, 3)
        tb = testBit(exemplar, 4)
        ts = testBit(exemplar, 5)

        # 文件上传
        path_cp = request.form.get("image_cp")
        path_bn = request.form.get("image_bn")
        path_kp = request.form.get("image_kp")
        path_md = request.form.get("image_md")
        path_tb = request.form.get("image_logo")
        path_ts = request.form.get("image_ts")

        # 添加插屏路径
        if cp != 0:
            if not path_cp:
                flash('请上传插屏图片')
                return render_template('/plugin/ad_add.html', target=target, target_logo=target_logo, packname=packname,
                                       productname=productname, contant=contant, contant_installed=contant_installed)

        # 添加开屏路径
        if kp != 0:
            if not path_kp:
                flash('请上传开屏图片')
                return render_template('/plugin/ad_add.html', target=target, target_logo=target_logo, packname=packname,
                                       productname=productname, contant=contant, contant_installed=contant_installed)

        # 添加广告条路径
        if bn != 0:
            if not path_bn:
                flash('请上传横屏图片')
                return render_template('/plugin/ad_add.html', target=target, target_logo=target_logo, packname=packname,
                                       productname=productname, contant=contant, contant_installed=contant_installed)

        # 添加富媒体路径
        if md != 0:
            if not path_md:
                flash('请上传视频图片')
                return render_template('/plugin/ad_add.html', target=target, target_logo=target_logo, packname=packname,
                                       productname=productname, contant=contant, contant_installed=contant_installed)

        # 添加图标路径
        if tb != 0:
            if not path_tb:
                flash('请上传logo图片')
                return render_template('/plugin/ad_add.html', target=target, target_logo=target_logo, packname=packname,
                                       productname=productname, contant=contant, contant_installed=contant_installed)

        # 添加推送路径
        if ts != 0:
            if not path_ts:
                flash('请上传推送图片')
                return render_template('/plugin/ad_add.html', arget=target, target_logo=target_logo, packname=packname,
                                       productname=productname, contant=contant, contant_installed=contant_installed)

        # 判断是否输入
        sql = "select * from advertisement where title='%s'" % (productname)
        checked = db.query(sql)
        if productname == '':
            return render_template('/plugin/ad_add.html', result='产品名为空', target=target, target_logo=target_logo,
                                   packname=packname, productname=productname, contant=contant,
                                   contant_installed=contant_installed)
        elif checked:
            return render_template('/plugin/ad_add.html', result='产品名已存在', target=target, target_logo=target_logo,
                                   packname=packname, productname=productname, contant=contant,
                                   contant_installed=contant_installed)
        elif packname == '':
            return render_template('/plugin/ad_add.html', result='包名为空', target=target, target_logo=target_logo,
                                   productname=productname, packname=packname, contant=contant,
                                   contant_installed=contant_installed)

        # 添加插件对应统一广告关系
        args_dict = {'product_id': w_id}
        args = _setArgs(args_dict)
        res = adm.product_list(args)
        data = json.loads(res).get('data')

        if data:
            sql = "insert into advertisement(title, title_acronym, w_id, package_name, target_type, target, target_logo, exemplar, html5, auto_download, contant, contant_installed, state, dev_type)  \
                    values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' ,'%s') returning id" \
                  % (
                      productname, title_acronym, w_id, packname, target_type, target, target_logo, exemplar, 0,
                      auto_download,
                      contant, contant_installed, state, dev_type)
            id = db.insert(sql)
            cp_id = data[0].get('cp_id')

            key = "plugin2zmns_" + str(id)
            value = [
                str(w_id),
                str(285),
                str(cp_id),
            ]
            value = "_".join(value)
            red.set(key, value)
        else:
            return render_template('/plugin/ad_add.html', result='查不到此统一id', target=target, target_logo=target_logo,
                                   productname=productname, packname=packname, contant=contant,
                                   contant_installed=contant_installed)

        # 判断素材种类
        if cp != 0:
            sql = "update advertisement set image_cp='%s' where id=%d" % (path_cp, id)
            db.execute(sql)
        if kp != 0:
            sql = "update advertisement set image_kp='%s' where id=%d" % (path_kp, id)
            db.execute(sql)
        if bn != 0:
            sql = "update advertisement set image_bn='%s' where id=%d" % (path_bn, id)
            db.execute(sql)
        if md != 0:
            sql = "update advertisement set image_md='%s' where id=%d" % (path_md, id)
            db.execute(sql)
        if tb != 0:
            sql = "update advertisement set image_logo='%s' where id=%d" % (path_tb, id)
            db.execute(sql)
        if ts != 0:
            sql = "update advertisement set image_push='%s' where id=%d" % (path_ts, id)
            db.execute(sql)

        # 上报素材库图片信息
        # binding_lst = set_image_lst(path_cp, path_kp, path_bn, path_md, path_tb, path_ts)
        # dict_args = {
        #     'binding_lst': binding_lst,
        #     'platform_id': 1,
        #     'ad_id': id,
        # }
        # res = Binding(json.dumps(dict_args))
        return render_template('/plugin/ad_add.html', step2='block', product=productname, step1='none')
    return render_template('/plugin/ad_add.html')


@ad_plugin.route('/', methods=['GET', 'POST'])
@ad_plugin.route('/plugin/ad_list', methods=['GET', 'POST'])
@login_required
def ad_list():
    ad_id = request.args.get('ad_id', '')
    ad_name = request.args.get('ad_name', '')
    w_title = request.args.get('w_title', '')
    ad_type = request.args.get('ad_type', '')
    dev_type = request.args.get('dev_type', '')
    bd_id = request.args.get('bd_id', '')
    state = request.args.get('state', '')
    page = int(request.args.get('page', 1))

    sql = "select * from advertisement where state != -1"
    if ad_id:
        sql += " and id='%s'" % (ad_id)
    if ad_name:
        sql += r" and title like '%s%s%s'" % ('%', ad_name, '%')
    if w_title:
        sql += r" and w_title like '%s%s%s'" % ('%', w_title, '%')
    if state:
        sql += " and state='%s'" % (state)
    if bd_id:
        sql += " and bd_id='%s'" % (bd_id)
    sql += " order by weights"
    query = db.query(sql)

    query = filter(lambda a: testBit(a.exemplar, int(ad_type)) != 0, query) if ad_type else query
    query = filter(lambda a: testBit(a.dev_type, int(dev_type)) != 0, query) if dev_type else query

    # 解析exemplar
    if query:
        for item in query:
            item.bd = bd_filter.get(item.get('bd_id'))
            item.dev_type = dev_type_filter(item.dev_type)
            item.target_type = 'wauee' if '.uzham.' in item.target else 'cp'

            res = testBit(item.exemplar, int(ad_type)) if ad_type else 1
            item.exemplar = exemplar_filter(item.exemplar)

    # 双重排序
    list = []
    for item in query:
        if item.state == 100:
            list.append(item)
            break
    for item in query:
        if item.state == 1:
            list.append(item)
    for item in query:
        if item.state == 0:
            list.append(item)

    pag = pagination.Pagination(list or [], page, 40)
    list = pag.list()

    if request.method == 'POST':
        for item in list:
            order = request.form.get(str(item.id))
            sql = "update advertisement set weights='%s' WHERE id='%s'" % (order, item.id)
            db.execute(sql)
        return redirect(url_for('ad_plugin.ad_list'))

    return render_template('/plugin/ad_list.html',
                           query=list,
                           ad_id=ad_id,
                           ad_name=ad_name,
                           ad_type=ad_type,
                           state=state,
                           pagination=pag,
                           w_title=w_title,
                           bd_id=bd_id,
                           bd_list=bd_filter,
                           dev_type_list=dev_type_dict,
                           dev_type=dev_type,
                           ad_type_dict=ad_type_dict)


@ad_plugin.route('/plugin/ad_list_zmns', methods=['GET', 'POST'])
@login_required
def ad_list_zmns():
    ad_id = request.args.get('ad_id', '')
    ad_name = request.args.get('ad_name', '')
    w_title = request.args.get('w_title', '')
    ad_type = request.args.get('ad_type', '')
    dev_type = request.args.get('dev_type', '')
    bd_id = request.args.get('bd_id', '')
    state = request.args.get('state', '')
    page = int(request.args.get('page', 1))

    sql = "select * from advertisement where state != -1"
    if ad_id:
        sql += " and id='%s'" % (ad_id)
    if ad_name:
        sql += r" and title like '%s%s%s'" % ('%', ad_name, '%')
    if w_title:
        sql += r" and w_title like '%s%s%s'" % ('%', w_title, '%')
    if state:
        sql += " and state='%s'" % (state)
    if bd_id:
        sql += " and bd_id='%s'" % (bd_id)
    sql += " order by weights"
    query = db.query(sql)

    query = filter(lambda a: testBit(a.exemplar, int(ad_type)) != 0, query) if ad_type else query
    query = filter(lambda a: testBit(a.dev_type, int(dev_type)) != 0, query) if dev_type else query

    # 解析exemplar
    if query:
        for item in query:
            item.bd = bd_filter.get(item.get('bd_id'))
            item.dev_type = dev_type_filter(item.dev_type)
            item.target_type = 'wauee' if '.uzham.' in item.target else 'cp'

            res = testBit(item.exemplar, int(ad_type)) if ad_type else 1
            item.exemplar = exemplar_filter(item.exemplar)

    # 双重排序
    list = []
    for item in query:
        if item.state == 100:
            list.append(item)
            break
    for item in query:
        if item.state == 1:
            list.append(item)
    for item in query:
        if item.state == 0:
            list.append(item)

    pag = pagination.Pagination(list or [], page, 40)
    list = pag.list()

    if request.method == 'POST':
        for item in list:
            order = request.form.get(str(item.id))
            sql = "update advertisement set weights='%s' WHERE id='%s'" % (order, item.id)
            db.execute(sql)
        return redirect(url_for('ad_plugin.ad_list'))

    # 统一广告接入
    request_args = {
        'status': '',
        'platform_id': 3,
    }
    request_args = receive_args(request_args)
    args = _setArgs(request_args)
    ad_lst = planList(args).get('data')
    if ad_lst:
        for item in ad_lst:
            item['bd'] = bd_filter.get(item.get('bd_id'))
            item['dev_type'] = dev_type_filter(item.get('match_app_type'))
    return render_template('/plugin/ad_list_zmns.html',
                           query=ad_lst,
                           ad_id=ad_id,
                           ad_name=ad_name,
                           ad_type=ad_type,
                           state=state,
                           pagination=pag,
                           w_title=w_title,
                           bd_id=bd_id,
                           bd_list=bd_filter,
                           dev_type_list=dev_type_dict,
                           dev_type=dev_type,
                           request_args=request_args)


@ad_plugin.route('/plugin/config', methods=['GET', 'POST'])
@login_required
def config():
    if request.method == 'POST':
        id = request.form.get('id') or ''
        auto_download = request.form.get('auto_download') or ''
        auto_icon = request.form.get('auto_icon') or ''
        show_interval = request.form.get('show_interval') or ''
        push_msg = request.form.get('push_msg') or ''
        push_msg_interval = request.form.get('push_msgInterval') or ''
        image_downloadText = request.form.get('image_downloadText') or ''
        auto_activeDays = request.form.get('auto_activeDays') or ''
        auto_installMins = request.form.get('auto_installMins') or ''
        sql = "update config set auto_download='%s', auto_icon='%s', show_interval='%s', push_msg='%s', \"image_downloadText\"='%s', \"push_msgInterval\"='%s', \"auto_activeDays\"='%s', \"auto_installMins\"='%s' " \
              "where id='%s'" % (
                  auto_download, auto_icon, show_interval, push_msg, image_downloadText, push_msg_interval,
                  auto_activeDays,
                  auto_installMins, id)
        db.execute(sql)

    sql = 'select * from config'
    query = db.query(sql)
    return render_template('/plugin/config.html', query=query)


@ad_plugin.route('/plugin/pure_plugin_edit', methods=['GET', 'POST'])
@login_required
def pure_plugin_edit():
    id = request.args.get('id')
    sql = "select * from advertisement where id=%s" % (id)
    query = db.query(sql)

    if request.method == 'POST':
        contant = request.form.get('contant', '')
        target = request.form.get('target', '')
        package_name = request.form.get('package_name', '')

        sql = "update advertisement set contant='%s', target='%s', package_name='%s' where id=%s" \
              % (contant, target, package_name, id)
        res = db.execute(sql)

        flash('修改成功', 'success') if res else flash('失败！', 'error')
        return redirect(url_for('ad_plugin.ad_list'))

    return render_template('/plugin/pure_plugin_edit.html',
                           query=query[0])


@ad_plugin.route('/plugin/edit', methods=['GET', 'POST'])
@login_required
def ad_edit():
    id = request.args.get('id')
    sql = "select * from advertisement where id=%s" % (id)
    query = db.query(sql)

    if request.method == 'POST':
        id = request.form.get('id')
        w_id = request.form.get('w_id') or ''
        title = request.form.get('title') or ''
        title_acronym = request.form.get('title_acronym') or ''
        contant = request.form.get('contant') or ''
        pack_name = request.form.get('package_name') or ''
        day_showtimes = request.form.get('day_showtimes') or ''
        day_showtimesCKP = request.form.get('day_showtimesCKP') or ''
        push_interval = request.form.get('push_interval') or ''
        exemplar_all = request.form.getlist('exemplar')
        exemplar = int(0)
        for item in exemplar_all:
            exemplar = exemplar + int(item)
        type_all = request.form.getlist('dev_type')
        dev_type = 0
        for item in type_all:
            dev_type += int(item)
        image_cp = request.form.get('image_cp') or ''
        image_kp = request.form.get('image_kp') or ''
        image_bn = request.form.get('image_bn') or ''
        image_md = request.form.get('image_md') or ''
        image_push = request.form.get('image_push') or ''
        image_cp_mn = request.form.get('image_cp_mn') or ''
        image_kp_mn = request.form.get('image_kp_mn') or ''
        image_bn_mn = request.form.get('image_bn_mn') or ''
        image_md_mn = request.form.get('image_md_mn') or ''
        image_push_mn = request.form.get('image_push_mn') or ''
        contant_installed = request.form.get('contant_installed') or ''
        image_logo = request.form.get('image_logo') or ''
        target_type = request.form.get('target_type') or ''
        target = request.form.get('target').replace('cdn1.zm.', 'cdn1.sdk.') or ''
        target_logo = request.form.get('target_logo') or ''
        state = request.form.get('state') or 0
        order = request.form.get('order') or ''
        auto_download = request.form.get('auto_download') or 0
        auto_install = request.form.get('auto_install') or 0
        auto_active = request.form.get('auto_active') or 0

        bn = cp = kp = md = tb = ts = 0
        bn = testBit(exemplar, 0)
        cp = testBit(exemplar, 1)
        kp = testBit(exemplar, 2)
        md = testBit(exemplar, 3)
        tb = testBit(exemplar, 4)
        if bn:
            if not image_bn:
                flash('请上传横屏图片')
                return redirect(url_for('ad_plugin.ad_edit', id=id))
        if cp:
            if not image_cp:
                flash('请上传插屏图片')
                return redirect(url_for('ad_plugin.ad_edit', id=id))
        if kp:
            if not image_kp:
                flash('请上传开屏图片')
                return redirect(url_for('ad_plugin.ad_edit', id=id))
        if md:
            if not image_md:
                flash('请上传视频图片')
                return redirect(url_for('ad_plugin.ad_edit', id=id))
        if tb:
            if not image_logo:
                flash('请上传logo图片')
                return redirect(url_for('ad_plugin.ad_edit', id=id))

        sql = "update advertisement set title='%s', title_acronym='%s', w_id='%s', contant='%s', package_name='%s', day_showtimes='%s', \"day_showtimesCKP\"='%s', push_interval='%s', exemplar='%s', image_cp='%s', image_kp='%s', image_bn='%s', " \
              "image_md='%s', image_push='%s', image_cp_mn='%s', image_kp_mn='%s', image_bn_mn='%s', image_md_mn='%s', image_push_mn='%s', image_logo='%s', target_type='%s', target='%s', target_logo='%s', state='%s', auto_download='%s', " \
              "auto_install='%s', auto_active='%s', contant_installed='%s', weights='%s', dev_type='%s' where id='%s'" \
              % (
                  title, title_acronym, w_id, contant, pack_name, day_showtimes, day_showtimesCKP, push_interval,
                  exemplar,
                  image_cp, image_kp, image_bn, image_md, image_push, image_cp_mn, image_kp_mn, image_bn_mn,
                  image_md_mn,
                  image_push_mn, image_logo, target_type, target, target_logo, state,
                  auto_download, auto_install, auto_active, contant_installed, order, dev_type, id)
        try:
            s = db.execute(sql)

            m_id = image_cp + '|' + image_bn + '|' + image_kp + '|' + image_md + '|' + image_push + '|' + image_logo
            args = "?ad_id=%s&platform_id=%s&ad_name=%s&m_id=%s" % (id, '1', title, m_id)
            res = Binding(args)
            flash('修改成功') if s else flash('修改失败')
        except Exception, e:
            print e, '------SQL_ERROR'

        # 上报素材库图片信息
        binding_lst = set_image_lst(image_cp, image_kp, image_bn, image_md, image_push, image_cp_mn,
                                    image_kp_mn, image_bn_mn, image_md_mn, image_push_mn, image_logo)
        dict_args = {
            'binding_lst': binding_lst,
            'platform_id': 1,
            'ad_id': id,
        }
        res = Binding(json.dumps(dict_args))

        # 上报更改记录
        if int(state) != query[0].get('state'):
            sql = "insert into operations (data_before, data_after, op_id, op_data_id, data_type, description)" \
                  " VALUES ('%s', '%s', %s, '%s', 0, 'state')" \
                  % (query[0].get('state') if query[0].get('state') == 0 else query[0].get('exemplar'),
                     state if state == 0 else exemplar, current_user.user_id, id)
            db.execute(sql)
        if int(exemplar) != query[0].get('exemplar'):
            sql = "insert into operations (data_before, data_after, op_id, op_data_id, data_type, description)" \
                  " VALUES ('%s', '%s', %s, '%s', 1, 'exemplar')" % (
                      query[0].get('exemplar'), exemplar, current_user.user_id, id)
            db.execute(sql)
        if int(auto_download) != query[0].get('auto_download'):
            sql = "insert into operations (data_before, data_after, op_id, op_data_id, data_type, description)" \
                  " VALUES ('%s', '%s', %s, '%s', 2, 'auto_download')" % (
                      query[0].get('auto_download'), auto_download, current_user.user_id, id)
            db.execute(sql)

        return redirect(url_for('ad_plugin.ad_list'))

    # 转换exemplar为二进制
    if query[0]:
        query[0]['exemplar'] = bin(query[0].get('exemplar'))
        query[0]['dev_type'] = bin(query[0].get('dev_type'))
    return render_template('/plugin/ad_edit.html',
                           query=query[0])


@ad_plugin.route('/plugin/source_select', methods=['GET', 'POST'])
@login_required
def source_select():
    id = request.args.get('id', '')
    if request.method == 'POST':
        image_id = request.form.getlist('image_id')
        image_id = '|'.join(image_id)
        ret = '''
            <script type="text/javascript">
                parent.selectImgCallBack(url='%s',id='%s');
                frameElement.api.close();
            </script>
            ''' % (image_id, id)
        return ret

    page = request.args.get('page', 1)
    name = request.args.get('name', '')
    dimension_id = request.args.get('dimension_id', '')
    second_type = request.args.get('second_type', '')
    first_type = request.args.get('first_type', '')

    arg = '?page=%s' % (int(page))
    dict_args = {
        'num': 30,
        'name': name,
        'dimension_id': dimension_id,
        'second_type': second_type,
        'first_type': first_type,
    }
    _arg = setArgs(dict_args)
    ret_arg = _arg + '&id=' + id
    args = arg + _arg

    res_type = GetTypes(args='')
    types = json.loads(res_type).get('type_list')
    res_dimension = GetDimensions()
    dimensions = json.loads(res_dimension).get('type_list')
    res_material = GetMaterials(args)
    materials = json.loads(res_material)

    sql = "select id, title from advertisement"
    query = db.query(sql)
    ad_list = {item.get('id'): item.get('title') for item in query}

    pagination = Pager(materials.get('materials'), getPageNum(page), 30, materials.get('count'))
    return render_template('/plugin/source_select.html',
                           types=types,
                           dimensions=dimensions,
                           materials=materials.get('materials'),
                           dimension_id=dimension_id,
                           second_type=second_type,
                           first_type=first_type,
                           name=name,
                           id=id,
                           args=ret_arg,
                           pagination=pagination,
                           ad_list=ad_list)


@ad_plugin.route('/plugin/second_type', methods=['GET', 'POST'])
@login_required
def second_type():
    first_type = request.args.get('first_type')

    args = "?id=%s" % (first_type)

    res_type = GetTypes(args)
    second_type = json.loads(res_type).get('type_list')[0].get('child')
    res = {
        'status': 200,
        'second_type': second_type
    }
    return json.dumps(res)


@ad_plugin.route('/plugin/img_url')
@login_required
def img_url():
    id = request.args.get('id')

    args = "?id=%s" % (id)

    res = GetImages(args)
    url = json.loads(res).get('urls')
    ret = {
        'status': 200,
        'url': url
    }
    return json.dumps(ret)


from ..utils.province import province_id_dict


@ad_plugin.route('/plugin/ad_plan', methods=['GET', 'POST'])
@login_required
def ad_plan():
    ad_id = request.args.get('ad_id', '')
    plan_id = request.args.get('plan_id', '')
    sql = "select a.*, b.title from ad_plan as a, advertisement as b where a.id=b.plan and b.id='%s'" % (ad_id)
    query = db.query(sql)
    if not query:
        sql = "insert into ad_plan (log_time) VALUES ('0') returning id"
        plan_id = db.insert(sql)
        sql = "update advertisement set plan='%s' where id='%s'" % (plan_id, ad_id)
        db.execute(sql)
        sql = "select a.*, b.title from ad_plan as a, advertisement as b where a.id=b.plan and b.id='%s'" % (ad_id)
        query = db.query(sql)[0]
    else:
        query = query[0]
    query['carrier'] = bin(query.get('carrier'))

    return render_template('/plugin/ad_plan.html',
                           query=query,
                           province_id_dict=province_id_dict)


@ad_plugin.route('/plugin/plan_edit', methods=['GET', 'POST'])
@login_required
def plan_edit():
    if request.method == 'POST':
        # 修改广告计划
        province_list = request.form.getlist('province_list')
        time_list = request.form.getlist('time_list')
        carrier_list = request.form.getlist('carrier_list')
        carrier = 0
        for item in carrier_list:
            carrier += int(item)
        plan_id = request.form.get('id') or ''

        province_list.append('0')
        time_list.append('0')

        province_array = "{" + ','.join(province_list) + "}"
        time_array = "{" + ','.join(time_list) + "}"

        # 更新计划
        sql = "update ad_plan set region_limit='%s', time_limit='%s', carrier='%s' where id='%s'" % (
            province_array, time_array, carrier, plan_id)
        s = db.execute(sql)
    if s:
        return '1'
    else:
        return ''


@ad_plugin.route('/plugin/delete_ad', methods=['GET', 'POST'])
@login_required
def delete_ad():
    ad_id = request.form.get('ad_id') or ''

    sql = "update advertisement set state='-1' WHERE id='%s'" % (ad_id)
    s = db.execute(sql)

    if s:
        return '1'
    else:
        return ''


@ad_plugin.route('/plugin/ad_data')
@login_required
def ad_data():
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    day = int(request.args.get('day') or 0)
    ad_id = request.args.get('ad_id') or ''
    ad_name = request.args.get('ad_name') or ''
    duration1 = request.args.get('duration1') or '60'
    duration2 = request.args.get('duration2') or '90'
    duration3 = request.args.get('duration3') or '300'
    duration4 = request.args.get('duration4') or '600'
    duration5 = request.args.get('duration5') or '1200'

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    sql = "select b.title, b.id, a.time, count(a.duration)c0, count(case when a.duration>= %s then 1 end)c1, count(case when a.duration>= %s then 1 end)c2, count(case when a.duration>= %s then 1 end)c3, count(case when a.duration>= %s then 1 end)c4, count(case when a.duration>= %s then 1 end)c5" \
          " from adself_data as a, advertisement as b " \
          "where a.ad_id=b.id and a.time>='%s' and a.time<='%s'" % (
              duration1, duration2, duration3, duration4, duration5, sdate, edate)
    sql += " and b.id=%s" % (ad_id) if ad_id else ''
    sql += " and title like '%s%s%s'" % ('%', ad_name, '%') if ad_name else ''
    sql += " group by b.title, b.id, a.time"
    query = db.query(sql)

    return render_template('/plugin/ad_data.html',
                           query=query,
                           sdate=sdate,
                           edate=edate,
                           ad_id=ad_id,
                           ad_name=ad_name,
                           duration1=round(float(duration1), 2),
                           duration2=round(float(duration2), 2),
                           duration3=round(float(duration3), 2),
                           duration4=round(float(duration4), 2),
                           duration5=round(float(duration5), 2))


@ad_plugin.route('/plugin/zmns_data')
@login_required
def zmns_data():
    ad_id = request.args.get('ad_id') or ''
    # title = request.args.get('title') or ''
    channel = request.args.get('channel') or ''
    # crm_id = request.args.get('crm_id') or ''
    ad_type = request.args.get('ad_type') or ''
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    sql = '''
        SELECT
            zmns.*, dev.dev, dev.channel as real_channel, count(*) over()
        FROM
            daily_data_zmns as zmns,
            developer as dev
        WHERE
            zmns.TYPE = 2
        AND zmns.TIME >= '%s'
        AND zmns.TIME <= '%s'
        AND zmns.app_id = dev.app_id
    ''' % (sdate, edate)

    total_sql = '''
    SELECT
        SUM (zmns.show) as sum_show,
        SUM (zmns.click) as sum_click,
        SUM (zmns.download) as sum_download,
        SUM (zmns.install) as sum_install,
        SUM (zmns.active) as sum_active
    FROM
        daily_data_zmns AS zmns,
        developer AS dev
    WHERE
        zmns. TYPE = 2
    AND zmns. TIME >= '%s'
    AND zmns. TIME <= '%s'
    AND zmns.app_id = dev.app_id
    ''' % (sdate, edate)
    if ad_id:
        sql += ' and zmns.ad_id = %s' % ad_id
        total_sql += ' and zmns.ad_id = %s' % ad_id
    if channel:
        sql += ' and dev.channel = %s' % channel
        total_sql += ' and dev.channel = %s' % channel
    if ad_type:
        sql += 'and zmns.ad_type = %s' % ad_type
        total_sql += 'and zmns.ad_type = %s' % ad_type
    query = db.query(sql)
    total_query = db.query(total_sql)
    plan_list = json.loads(adm.plan_list())
    plan_list = plan_list.get('data', [])
    plan_dict = {item.get('plan_id'): item.get('plan_name') for item in plan_list}

    def group_by(l, arg, data_callback):
        return [dict(dict(data=data_callback(group)), **dict(zip(tuple(arg), name))) for name, group in
                groupby(l, key=lambda x: tuple(x[y] for y in arg))]

    if query:
        query = sorted(query, key=lambda x: (x['time'], x['real_channel'], x['dev']), reverse=True)
        query = group_by(query, ['time'],
                         lambda l: group_by(l, ['real_channel', 'dev'],
                                            lambda l: list(l)))
        for grand in query:
            grand['show'] = 0
            grand['click'] = 0
            grand['download'] = 0
            grand['install'] = 0
            grand['active'] = 0
            for parent in grand.get('data'):
                parent['show'] = 0
                parent['click'] = 0
                parent['download'] = 0
                parent['install'] = 0
                parent['active'] = 0
                for child in parent.get('data'):
                    parent['show'] += child['show']
                    parent['click'] += child['click']
                    parent['download'] += child['download']
                    parent['install'] += child['install']
                    parent['active'] += child['active']
                grand['show'] += parent['show']
                grand['click'] += parent['click']
                grand['download'] += parent['download']
                grand['install'] += parent['install']
                grand['active'] += parent['active']
    return render_template('plugin/zmns_data.html',
                           query=query,
                           plan_dict=plan_dict,
                           ad_id=ad_id,
                           channel=channel,
                           ad_type=ad_type,
                           sdate=sdate,
                           edate=edate,
                           crm_list=crm_filter,
                           ad_type_dict=ad_display_type,
                           total_query=total_query[0])


@ad_plugin.route('/plugin/data')
@login_required
def data():
    ad_id = request.args.get('ad_id') or ''
    title = request.args.get('title') or ''
    channel = request.args.get('channel') or ''
    crm_id = request.args.get('crm_id') or ''
    ad_type = request.args.get('ad_type') or ''
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    page = int(request.args.get('page') or 1)
    day = int(request.args.get('day') or 0)

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    # sql = "select a.*, b.crm_id from \
    #         (select a.*, COALESCE(b.count,0) as p_active from daily_data_ns as a left join \
    #         (select count(duration), ad_id, d.app_id, time, crm_id from adself_data ,developer as d where time>='%s' and time<='%s' \
    #         group by ad_id, d.app_id, time, crm_id) as b \
    #         on a.app_id=b.app_id and a.ad_id=b.ad_id and a.time=b.time) as a \
    #         left join developer as b on a.app_id = b.app_id \
    #         where a.time>='%s' and a.time<='%s'" % (sdate, edate, sdate, edate)
    sql = "select a.*, b.crm_id, c.title, count(*) over() \
            from daily_data_ns as a, developer as b, advertisement as c \
            where a.time>='%s' and a.time<='%s' and \
            a.app_id = b.app_id and a.ad_id = c.id" % (sdate, edate)

    sum_sql = '''
        SELECT
            a.ad_type,
            SUM (show) AS show,
            SUM (click) AS click,
            SUM (download) AS download,
            SUM (install) AS install,
            SUM (active) AS active
        FROM
            daily_data_ns AS a,
            developer AS b,
            advertisement AS c
        WHERE
            a.time >= '%s'
        AND a.time <= '%s'
        AND a.app_id = b.app_id
        AND a.ad_id = c.id
        ''' % (sdate, edate)

    dict_args = {
        'ad_id': ad_id,
        'title': title,
        'channel': channel,
        'crm_id': crm_id,
        'ad_type': ad_type,
        'sdate': sdate,
        'edate': edate
    }
    args = setArgs(dict_args)

    if ad_id:
        sql += ' and a.ad_id=%s' % ad_id
        sum_sql += ' and a.ad_id=%s' % ad_id
    if title:
        sql += " and c.title like '%s%s%s'" % ('%', title, '%')
        sum_sql += " and c.title like '%s%s%s'" % ('%', title, '%')
    if channel:
        sql += " and a.channel='%s'" % channel
        sum_sql += " and a.channel='%s'" % channel
    if crm_id:
        sql += " and b.crm_id='%s'" % crm_id
        sum_sql += " and b.crm_id='%s'" % crm_id
    if ad_type:
        sql += " and a.ad_type='%s'" % ad_type
        sum_sql += " and a.ad_type='%s'" % ad_type

    sql += " LIMIT 50 OFFSET 50 * %s" % (page - 1)
    sum_sql += " group by ad_type"

    query = db.query(sql)
    sum_value = db.query(sum_sql)

    sum_show = sum_click = sum_download = sum_install = sum_active = silent_download = 0
    click_rate = download_rate = install_rate = 0
    if sum_value:
        for item in sum_value:
            sum_show += item['show']
            sum_click += item['click']
            sum_download += item['download']
            sum_install += item['install']
            sum_active += item['active']
            if item['ad_type'] == 6:
                silent_download = item['download']
        click_rate = float(sum_click) / sum_show * 100 if sum_show else 0
        download_rate = (float(sum_download) - float(silent_download)) / sum_click * 100 if sum_click else 0
        install_rate = float(sum_install) / sum_download * 100 if sum_download else 0

    if query:
        for item in query:
            item['click_rate'] = float(item.click) / item.show * 100 if item.show else 0
            item['install_rate'] = float(item.install) / item.show * 100 if item.show else 0

    pag = pagination.Pagination(query or [], page, 50, query[0].count if query else None)
    list = pag.list()

    # sql = "select id, title from advertisement"
    # ad_list = db.query(sql)
    # ad_list = {item.get('id'): item.get('title') for item in ad_list}

    sql = "select id, dev from developer"
    dev_list = db.query(sql)
    dev_list = {item.get('id'): item.get('dev') for item in dev_list}

    return render_template('plugin/dev_data.html',
                           ad_id=ad_id,
                           title=title,
                           crm_id=crm_id,
                           sdate=sdate,
                           edate=edate,
                           pagination=pag,
                           list=list,
                           args=args,
                           channel=channel,
                           ad_type=ad_type,
                           sum_install=sum_install,
                           sum_click=sum_click,
                           sum_show=sum_show,
                           sum_active=sum_active,
                           sum_download=sum_download,
                           silent_download=silent_download,
                           click_rate=click_rate,
                           install_rate=install_rate,
                           download_rate=download_rate,
                           # download_rate2=download_rate2,
                           # active_rate=active_rate,
                           crm_list=crm_filter,
                           # ad_list=ad_list,
                           dev_list=dev_list,
                           ad_type_dict=ad_type_dict)


@ad_plugin.route('/plugin/data_warning')
@login_required
def data_warning():
    channel = request.args.get('channel', '')
    num = request.args.get('num') or 15
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    day = int(request.args.get('day') or 0)
    type = request.args.get('type') or '0'

    channel_dict = {}

    if type == '0':
        data_type = 'phone_type'
    elif type == '1':
        data_type = 'location'
    elif type == '2':
        data_type = 'network'
    elif type == '3':
        data_type = 'install_distribution'
    elif type == '4':
        data_type = 'install_active'
    elif type == '5':
        data_type = 'sim_has'
    elif type == '6':
        data_type = 'sdk_version'
    elif type == '7':
        data_type = 'carrier'

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    if type == '0' or '2' or '7':
        if channel:
            sql = "select count(a.*) as value, a.%s as name, b.channel " \
                  "from phone_info as a, developer as b " \
                  "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s'and b.channel='%s' " \
                  "group by %s, b.channel " \
                  "order by value" \
                  % (data_type, sdate, edate, channel, data_type)
        else:
            sql = "select count(a.*) as value, a.%s as name " \
                  "from phone_info as a, developer as b " \
                  "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s' " \
                  "group by %s " \
                  "order by value" % (data_type, sdate, edate, data_type)

    if type == '1':
        if channel:
            sql = "select count(a.*) as value, left(a.%s, 2) as name, b.channel " \
                  "from phone_info as a, developer as b " \
                  "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s'and b.channel='%s' " \
                  "group by b.channel, left(%s, 2) " \
                  "order by value" \
                  % (data_type, sdate, edate, channel, data_type)
        else:
            sql = "select count(a.*) as value, left(a.%s, 2) as name " \
                  "from phone_info as a, developer as b " \
                  "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s' " \
                  "group by left(%s, 2) " \
                  "order by value" % (data_type, sdate, edate, data_type)

    if type == '3':
        sql = "select sum(install) as value, channel, ad_name as name " \
              "from daily_data_ns " \
              "where channel = '%s' and time>='%s' and time<='%s' " \
              "group by channel, ad_name " \
              "order by value" % (channel, sdate, edate) if channel else ''
    elif type == '4':
        sql = "select cast(sum(a.install) as float)/(case when sum(b.active_new)=0 then 1 else sum(b.active_new) end) as value, a.channel as name " \
              "from daily_data_ns as a, dev_clearing as b " \
              "where a.channel=b.channel and a.time=b.time and a.time>='%s' and a.time<='%s' " \
              "group by a.channel " \
              "order by value" % (sdate, edate)
    elif type == '6':
        if channel:
            sql = "select count(a.*) as value, a.%s as name, b.channel " \
                  "from phone_info as a, developer as b " \
                  "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s'and b.channel='%s' " \
                  "group by %s, b.channel " \
                  "order by value" \
                  % (data_type, sdate, edate, channel, data_type)
        else:
            sql = "select count(a.*) as value, a.%s as name " \
                  "from phone_info as a, developer as b " \
                  "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s' " \
                  "group by %s " \
                  "order by value" % (data_type, sdate, edate, data_type)

        sql_v = "select distinct sdk_version, channel from phone_info as a, developer as b " \
                "where a.app_id = b.app_id and a.time>='%s' and a.time<='%s' " \
                "order by sdk_version desc" \
                % (sdate, edate)
        channel_list = db.query(sql_v)

        for dic in channel_list:
            if dic['sdk_version'] in channel_dict:
                channel_dict[dic['sdk_version']] += ' / ' + str(dic['channel'])
            else:
                channel_dict[str(dic['sdk_version'])] = str(dic['channel'])

    query = db.query(sql)

    if type == '5':
        sql = "select count(case when a.imsi='null' then 1 end) as no, count(case when a.imsi!='null' then 1 end)has, channel " \
              "from phone_info as a, developer as b " \
              "where a.app_id=b.app_id and channel = '%s' and time>='%s' and time<='%s' " \
              "group by channel" % (channel, sdate, edate) if channel else ''
        query = db.query(sql)

        query = [{'name': '有SIM', 'value': query[0].get('has')},
                 {'name': '无SIM', 'value': query[0].get('no')}] if query else ''

    if type == '7':
        if query:
            for item in query:
                item['name'] = carrier_filter.get(item['name'])

    # 计算总值
    sum = 0
    if type == '4':
        sum = 1
    elif query:
        for item in query:
            sum += item.get('value')

    query = query[-int(num):] if query else []

    # 查询预警水位
    sql = "select %s from warning_area" % (data_type)
    warning_area = getattr(db.query(sql)[0], data_type)
    return render_template('plugin/data_warning.html',
                           channel=channel,
                           sdate=sdate,
                           edate=edate,
                           query=query,
                           type=type,
                           num=num,
                           sum=sum,
                           warning_area=warning_area,
                           channel_dict=channel_dict)


@ad_plugin.route('/plugin/warning_area', methods=['GET', 'POST'])
@login_required
def warning_area():
    if request.method == 'POST':
        phone_type = request.form.get('phone_type', '60')
        location = request.form.get('location', '20')
        network = request.form.get('network', '50')
        install_distribution = request.form.get('install_distribution', '40')
        install_active = request.form.get('install_active', '50')
        sim_has = request.form.get('sim_has', '50')

        sql = '''update warning_area set phone_type=%s, location=%s, network=%s,
              install_distribution=%s, install_active=%s, sim_has=%s''' % (
            phone_type, location, network, install_distribution, install_active, sim_has)
        r = db.execute(sql)
        flash('更改成功！') if r else flash('失败！', category='warning')
        return redirect(url_for('ad_plugin.data_warning'))
    sql = "select * from warning_area"
    query = db.query(sql)[0]
    return render_template('plugin/warning_area.html',
                           query=query)


@ad_plugin.route('/plugin/op_record')
@login_required
def op_record():
    channel = request.args.get('channel', '')
    switch = request.args.get('switch', '')
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    day = int(request.args.get('day') or 0)
    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    sql = '''
    SELECT op.*,
           dev.dev
    FROM dev_operation AS op,
         developer AS dev
    WHERE time>='%s'
      AND time<='%s'
      AND op.channel = dev.channel
        ''' % (sdate, edate)
    if channel:
        sql += " and channel='%s'" % (channel)
    if switch:
        sql += " and switch='%s'" % (switch)

    query = db.query(sql)
    if query:
        for item in query:
            item['timestamp'] = str(item['timestamp'])[:8]
    return render_template('plugin/op_record.html',
                           query=query,
                           channel=channel,
                           switch=switch,
                           sdate=sdate,
                           edate=edate)


@ad_plugin.route('/plugin/channel', methods=['GET', 'POST'])
@login_required
def channel():
    if request.method == 'POST':
        # 添加app_id和dev
        base = 10000
        dev = request.form.get('dev', '').replace(' ', '')
        dev_type = request.form.get('dev_type', '')
        if dev == '':
            return redirect(url_for('ad_plugin.channel'))

        sql = "select dev from developer where dev='%s'" % (dev)
        query = db.query(sql)
        if query:
            flash('该开发者已存在')
            return redirect(url_for('ad_plugin.channel'))

        app_id = uuid.uuid1()
        # 记录user_id
        if dev[0] == 'F':
            part = dev.split('_')
            user_id = part[1]
        else:
            user_id = '0'
        sql = "insert into developer (dev, type, app_id, user_id, state, crm_id) VALUES ('%s', '%s', '%s', '%s', '1', '%s')" \
              % (dev, dev_type, app_id, user_id, current_user.user_id)
        db.execute(sql)

        # 更新渠道号
        sql = "select id from developer where app_id='%s'" % (app_id)
        channel = db.query(sql)[0].id + base
        sql = "update developer set channel='%s' where app_id='%s'" % (channel, app_id)
        db.execute(sql)
        flash('添加成功')
        return redirect(url_for('ad_plugin.channel'))

    channel = (request.args.get('channel', '')).replace(' ', '')
    user_id = (request.args.get('user_id') or '').replace(' ', '')
    app_id = (request.args.get('app_id') or '').replace(' ', '')
    dev_type = (request.args.get('dev_type') or '').replace(' ', '')
    crm_id = (request.args.get('crm_id') or '').replace(' ', '')
    dev = (request.args.get('dev') or '').replace(' ', '')
    order = (request.args.get('order') or 'id')
    page = int(request.args.get('page') or 1)
    sql = "select a.*, COALESCE(b.active_new,0) as active_new from developer as a " \
          "left join plgin_data as b on a.id=b.dev_id and b.time='%s'" % (g.now)

    args = {
        'channel': channel,
        'user_id': user_id,
        'app_id': app_id,
        'type': dev_type,
        'crm_id': crm_id,
        'dev': dev
    }
    dict_args = {
        'a.channel': channel,
        'a.user_id': user_id,
        'a.app_id': app_id,
        'a.type': dev_type,
        'a.crm_id': crm_id
    }
    if dev:
        sql += " where a.dev like '%" + dev + "%'"
    sql = setSQL(sql, dict_args)
    sql += ''' ORDER by %s desc''' % (order)
    query = db.query(sql)

    pag = pagination.Pagination(query or [], page, 20)
    query = pag.list()

    # dev_type转义

    def func(x):
        x['dev_type'] = dev_type_filter(x.get('type'))
        return x

    query = map(func, query)
    return render_template('plugin/channel.html',
                           query=query,
                           args=setArgs(args),
                           channel=channel,
                           user_id=user_id,
                           app_id=app_id,
                           pagination=pag,
                           dev_type_list=dev_type_dict,
                           dev_type=dev_type,
                           crm_list=crm_filter,
                           crm_id=crm_id,
                           order=order)


@ad_plugin.route('/plugin/dev_plan', methods=['GET', 'POST'])
def dev_plan():
    channel = request.args.get('channel', '')
    plan_id = request.args.get('plan_id', '')
    sql = "select a.*, b.dev from ad_plan as a, developer as b where a.id=b.plan_id and b.channel='%s'" % (channel)
    query = db.query(sql)
    if not query:
        sql = "insert into ad_plan (log_time) VALUES ('0') returning id"
        plan_id = db.insert(sql)
        sql = "update developer set plan_id='%s' where channel='%s'" % (plan_id, channel)
        db.execute(sql)
        sql = "select a.*, b.dev from ad_plan as a, developer as b where a.id=b.plan_id and b.channel='%s'" % (channel)
        query = db.query(sql)[0]
    else:
        query = query[0]

    return render_template('/plugin/dev_plan.html',
                           query=query,
                           province_id_dict=province_id_dict)


@ad_plugin.route('/dev_edit', methods=['GET', 'POST'])
def dev_edit():
    exemplar_max = 4294967295 - 511
    channel = request.args.get('channel')

    if request.method == 'POST':
        logo_num = (request.form.get('logo_num') or 0).replace(' ', '')
        push_msg_interval = (request.form.get('push_msg_interval') or 0).replace(' ', '')
        bn_msg_interval = (request.form.get('bn_msg_interval') or 0).replace(' ', '')
        md_msg_interval = (request.form.get('md_msg_interval') or 0).replace(' ', '')
        cp_msg_interval = (request.form.get('cp_msg_interval') or 0).replace(' ', '')
        kp_msg_interval = (request.form.get('kp_msg_interval') or 0).replace(' ', '')
        logo_msg_interval = (request.form.get('logo_msg_interval') or 0).replace(' ', '')
        xtts_msg_interval = (request.form.get('xtts_msg_interval') or 0).replace(' ', '')
        xtts2_msg_interval = (request.form.get('xtts2_msg_interval') or 0).replace(' ', '')
        ad_show_mode = int(request.form.get('ad_show_mode', 0))
        type = (request.form.get('type') or 0).replace(' ', '')
        source_type = (request.form.get('source_type') or 0).replace(' ', '')
        quality = request.form.get('quality', '2')
        install_interface = request.form.get('install_interface', '0')
        gdt_thdflag = int(request.form.get('gdt_thdflag', 0))
        xf_thdflag = int(request.form.get('xf_thdflag', 0))
        thdflag = gdt_thdflag + xf_thdflag * 2
        exemplar_list = request.form.getlist('exemplar')
        exemplar = 0
        for item in exemplar_list:
            exemplar += int(item)
        sql = "update developer " \
              "set exemplar='%s', logo_num='%s', push_msg_interval='%s', bn_msg_interval='%s'," \
              " md_msg_interval='%s', cp_msg_interval='%s', kp_msg_interval='%s', logo_msg_interval='%s'," \
              " xtts_msg_interval='%s',type='%s', xtts2_msg_interval='%s', source_type='%s', quality='%s'," \
              " install_interface='%s', thdflag='%s', ad_show_mode='%s'" \
              " where channel='%s'" % (
                  exemplar, logo_num, push_msg_interval, bn_msg_interval, md_msg_interval, cp_msg_interval,
                  kp_msg_interval, logo_msg_interval, xtts_msg_interval, type, xtts2_msg_interval, source_type, quality,
                  install_interface, thdflag, ad_show_mode, channel)
        s = db.execute(sql)
        flash('更改成功！') if s else flash('更改失败！')
        return redirect(url_for('ad_plugin.channel'))

    sql = "select * from developer where channel='%s'" % (channel)
    query = db.query(sql)[0]
    query['gdt_thdflag'] = query['thdflag'] % 2
    query['xf_thdflag'] = query['thdflag'] >> 1
    exemplar = bin(long(query.get('exemplar')))
    return render_template('plugin/dev_edit.html',
                           query=query,
                           exemplar=exemplar)


@ad_plugin.route('/plugin/jar_download', methods=['GET', 'POST'])
@login_required
def jar_download():
    if request.method == 'POST':
        url = request.form.get('head_img0')
        version = request.form.get('version')
        description = request.form.get('description')
        sql = "insert into plgin_version (version, url, description) VALUES ('%s', '%s', '%s')" % (
            version, url, description)
        s = db.execute(sql)
        flash('成功！', 'positive') if s else flash('失败！', 'negative')
        return redirect(url_for('ad_plugin.jar_download'))
    sql = 'select * from plgin_version order by id DESC'
    query = db.query(sql)
    return render_template('/plugin/jar_download.html',
                           query=query)


@ad_plugin.route('/plugin/sdk')
@login_required
def sdk():
    channel = request.args.get('channel') or ''
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    day = int(request.args.get('day') or 0)

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    sql = "select a.*, b.channel from plgin_data as a, developer as b where a.app_id=b.app_id and time>='%s' and time<='%s'" % (
        sdate, edate)

    sql += " and b.channel=%s" % (channel) if channel else ''
    query = db.query(sql)

    total = 0
    if query:
        for item in query:
            total += item['active_new']
    return render_template('/plugin/sdk.html',
                           query=query,
                           sdate=sdate,
                           edate=edate,
                           total=total,
                           channel=channel)


@ad_plugin.route('/upload', methods=['POST'])
@login_required
def upload():
    d = request.form.to_dict()
    d.update({'filename': request.files.values()[0].filename})
    response = requests.post('http://yun.wauee.com/upload',
                             data=d,
                             files=request.files)
    return response.text


@ad_plugin.route('/plugin/clearing', methods=['GET', 'POST'])
@login_required
def clearing():
    earnings = request.form.get('earnings') or 0
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    day = int(request.args.get('day') or 0)

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    # #读取第一次写入数据库
    # for item in query:
    #     sql = "select * from dev_clearing where time = '%s' and channel = '%s'" % (item.time, item.channel)
    #     query2 = db.query(sql)
    #     earnings_install = arpu_install * item.install
    #     if not query2:
    #         sql = "insert into dev_clearing (dev_id, app_id, channel, active_new, install, install_sim, earnings_install, arpu_install, time)" \
    #               "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    #                   item.dev_id, item.app_id, item.channel, item.active_new, item.install, item.install_sim, earnings_install,
    #                   arpu_install,
    #                   item.time)
    #         db.execute(sql)
    #     else:
    #         if query2[0].install != item.install or query2[0].active_new != item.active_new or query2[0].install_sim != item.install_sim:
    #             sql = "update dev_clearing set install='%s', install_sim='%s', active_new='%s'  " \
    #                   "WHERE time='%s' and channel='%s'" % (item.install, item.install_sim, item.active_new, item.time, item.channel)
    #             db.execute(sql)

    if request.method == 'POST':
        # 查询统计
        sql = '''select * from dev_clearing where time>='%s' and time<='%s' and install != 0 ''' % (sdate, edate)
        query = db.query(sql)

        sum_install = 0
        for item in query:
            sum_install += item.install

        arpu_install_ = round(float(earnings) / sum_install, 3) if sum_install != 0 else float(earnings)
        arpu_install = arpu_install_ * 0.7

        # 预收写入数据库
        earnings_install_add = 0
        for item in query:
            earnings_install = arpu_install * item.install if item != query[len(query) - 1] else float(
                earnings) * 0.7 - earnings_install_add
            earnings_install_add += earnings_install

            if earnings and earnings != '0.0':
                sql = "update dev_clearing set arpu_install='%s', earnings_install='%s'" \
                      "WHERE time='%s' and channel='%s'" % (arpu_install, earnings_install, item.time, item.channel)
            x = db.execute(sql)
            if not x:
                print x

                # if request.form.get('excel') == u'导出':
                #     data = []
                #     data.append([u'开发者', u'渠道号', u'日期', u'预返金额', u'预返个数'])
                #     sql = "select * from dev_clearing WHERE time>='%s' and time<='%s'" % (sdate, edate)
                #     query = db.query(sql)
                #     for item in query:
                #         sql = "select dev from developer where id='%s'" % (item.dev_id)
                #         query2 = db.query(sql)
                #         item['dev'] = query2[0].dev if query2 else item.dev_id
                #         s = [item.dev, item.channel, str(item.time), item.earnings_pre,
                #              round(float(item.earnings_pre) / 0.8, 0)]
                #         data.append(s)
                #
                #     output = excel.make_response_from_array(data, 'csv')
                #     output.headers["Content-Disposition"] = "attachment; filename=1.csv".format(str(g.now))
                #     output.headers["Content-type"] = "text/csv"
                #     return output

    sql = '''
        SELECT a.*,
       b.active FROM
  (SELECT a.*, b.dev, c.active_sim as sdk_active_sim, c.active_showad, c.active_new AS active_new2, count(*) over()
   FROM dev_clearing AS a, developer AS b, plgin_data AS c
   WHERE a.time >= '%s'
     AND a.time <= '%s'
     AND CAST (a.dev_id AS INT) = b.id
     AND c.time = a.time
     AND CAST (a.dev_id AS INT) = c.dev_id
        ''' % (sdate, edate)
    sum_sql = '''
        SELECT SUM(a.install) AS install,
               SUM(a.install_sim) AS install_sim,
               SUM(a.active_sim) AS active_sim,
               SUM(a.arpu_install) AS arpu_install,
               SUM(a.earnings_pre) AS payment,
               SUM(a.earnings_install) AS income,
               SUM(c.active_new) AS active_new,
               SUM(c.active_sim) AS sdk_active_sim,
               SUM(c.active_showad) AS active_showad
        FROM dev_clearing AS a,
             developer AS b,
             plgin_data AS c
        WHERE a.time >= '%s'
          AND a.time <= '%s'
          AND CAST (a.dev_id AS INT) = b.id
          AND c.time = a.time
          AND CAST (a.dev_id AS INT) = c.dev_id
        ''' % (sdate, edate)
    # sql = "select a.*, b.dev " \
    #       "from dev_clearing as a, developer as b " \
    #       "WHERE a.time>='%s' and a.time<='%s' and cast(a.dev_id as int)=b.id" % (sdate, edate)
    channel = request.args.get('channel', '').replace(' ', '')
    user_id = request.args.get('user_id', '').replace(' ', '')
    crm_id = request.args.get('crm_id', '')
    no_install = request.args.get('no_install')
    page = int(request.args.get('page') or 1)
    if channel:
        sql += " and a.channel='%s'" % (channel)
        sum_sql += " and a.channel='%s'" % (channel)
    if crm_id:
        sql += " and b.crm_id=%s" % (crm_id)
        sum_sql += " and b.crm_id=%s" % (crm_id)
    if user_id:
        sql += " and b.dev like '%s%s%s'" % ('%', user_id, '%')
        sum_sql += " and b.dev like '%s%s%s'" % ('%', user_id, '%')
    if no_install:
        sql += " and a.install=0"
        sum_sql += " and a.install=0"
    sql += ''' ORDER BY c.active_new DESC LIMIT 50
               OFFSET 50 * %s) AS a,

              (SELECT sum(active) AS active,
                      app_id,
                      TIME
               FROM daily_data_ns
               WHERE TIME >= '%s'
                 AND TIME <= '%s'
               GROUP BY app_id,
                        TIME) AS b
            WHERE a.app_id=b.app_id
              AND a.time=b.time''' % (page - 1, sdate, edate)
    query = db.query(sql)
    sum_list = db.query(sum_sql)

    # sum_install_price = 0
    # sum_earning = 0
    # sum_user = 0
    # sum_install = 0
    # list1 = []
    # list2 = []

    if query:
        for item in query:
            # sum_earning += item.earnings_install
            # sum_install_price += item.earnings_pre
            # sum_user += item.active_new2
            # sum_install += item.install
            item['earnings_install'] = item.get('arpu_install') * item.get('install_sim')
            item['real_arpu_install'] = item.earnings_pre / item.install_sim if item.install_sim else item.earnings_pre
            item['real_arpu_active_new'] = item.earnings_pre / item.active_new if item.active_new else item.earnings_pre
            # item['active_sim'] = item.get('active_sim') or 0
            # item['active_showad'] = item.get('active_showad') or 0
            # 隐藏新增安装为0
            # if item.install == 0 and item.active_new == 0:
            #     list2.append(item)
            # else:
            #     list1.append(item)
    if sum_list:
        for item in sum_list:
            for k, v in item.items():
                if not v:
                    item[k] = 0
            item['income'] = float(item['income']) / 0.7
            item['arpu_install'] = item['income'] * 0.85 / float(item['install']) if item['install'] else 0
    # sum_earning = float(sum_earning) / 0.7
    # arpu = sum_earning * 0.85 / float(sum_install) if sum_install else 0

    # 获取adm收入
    dict_args = {
        'sdate': sdate,
        'edate': edate,
        'platform_id': 3,
    }
    res = adm.earnings_list(_setArgs(dict_args))
    data = json.loads(res).get('data')
    adm_earnings = 0.0
    if data:
        for item in data:
            adm_earnings += item.get('money')

    # 分页
    dict_args = {
        'channel': channel,
        'sdate': sdate,
        'edate': edate,
        'user_id': user_id,
        'crm_id': crm_id,
        'no_install': no_install
    }
    args = setArgs(dict_args)
    pag = pagination.Pagination(query or [], page, 50, query[0].count if query else None)

    return render_template('plugin/clearing.html',
                           earnings=float(earnings),
                           query=query,
                           args=args,
                           pagination=pag,
                           dict_args=dict_args,
                           # query2=list2,
                           # sum_user=sum_user,
                           # sum_install=sum_install,
                           # sum_install_price=sum_install_price,
                           # sdate=sdate,
                           # edate=edate,
                           # sum_earning=sum_earning,
                           # channel=channel,
                           sum_list=sum_list[0],
                           # arpu=arpu,
                           # user_id=user_id,
                           # crm_id=crm_id,
                           crm_list=crm_filter,
                           adm_earnings=adm_earnings)


@ad_plugin.route('/plugin/arpu_active_new_details', methods=['GET', 'POST'])
@login_required
def arpu_active_new_details():
    channel = request.args.get('channel')
    date = request.args.get('date')
    sdate = datetime.datetime.strptime(date, '%Y-%m-%d') - datetime.timedelta(days=6)
    sql = '''
        SELECT
            a.*, b.dev
        FROM
            dev_clearing AS a,
            developer AS b
        WHERE
            CAST (a.dev_id AS INT) = b.id
        AND a.time >= '%s'
        AND a.time <= '%s'
        AND a.channel = %s
        ORDER BY a.time DESC
        ''' % (sdate, date, channel)
    query = db.query(sql)

    if query:
        for item in query:
            item['earnings_install'] = item.get('arpu_install') * item.get('install_sim')
            item['real_arpu_install'] = item.earnings_pre / item.install_sim if item.install_sim else item.earnings_pre
            item['real_arpu_active_new'] = item.earnings_pre / item.active_new if item.active_new else item.earnings_pre

    return render_template('plugin/arpu_active_new_details.html',
                           query=query)


@ad_plugin.route('/plugin/pre_post', methods=['GET', 'POST'])
def pre_post():
    id = request.form.get('id')
    pre = request.form.get('pre')
    sql = "update dev_clearing set earnings_pre='%s' WHERE id='%s'" % (pre, id)
    res = db.execute(sql)
    if res:
        return json.dumps({'success': 1})


@ad_plugin.route('/plugin/clearing_detail')
@login_required
def clearing_detail():
    channel = request.args.get('channel')
    time = request.args.get('time')

    point = '2017-12-27'
    if time < point:
        sql = '''
            SELECT
                adv.title AS ad_name,
                ns.ad_id,
                dev.dev,
                dev.type,
                SUM (ns.install) AS install,
                SUM (da.install) AS valid_install,
                adv.dev_type
            FROM
                daily_data_ns AS ns,
                advertisement AS adv,
                daily_data_detail AS da,
                developer AS dev
            WHERE
                ns.channel = '%s'
            AND ns.time = '%s'
            AND ns.install != 0
            AND ns.ad_id = adv.id
            AND da.dailydata_id = ns.id
            AND dev.id = ns.dev_id
            GROUP BY
                ns.ad_id,
                adv.title,
                adv.dev_type,
                dev.dev,
                dev.type
            ''' % (channel, time)
    else:
        sql = '''
        SELECT * FROM
        (
        SELECT dev.dev,
               dev.app_id,
               dev.channel,
               dev.type as dev_type,
               zmns.ad_id,
               zmns.ad_type,
               zmns.type AS zmns_type,
               SUM(zmns.install) as install
        FROM developer AS dev,
             daily_data_zmns AS zmns
        WHERE zmns.type = 0
          AND zmns.time = '%s'
          AND dev.channel = '%s'
          AND dev.app_id = zmns.app_id
        GROUP BY dev.dev,
                 dev.app_id,
                 dev.channel,
                 dev.type,
                 zmns.ad_id,
                 zmns.ad_type,
                 zmns.type
        ) as a
        LEFT JOIN
        (
        SELECT dev.app_id,
               zmns.ad_type,
               zmns.ad_id,
               SUM(zmns.install) as valid_install
        FROM developer AS dev,
             daily_data_zmns AS zmns
        WHERE zmns.type = 2
          AND zmns.time = '%s'
          AND dev.channel = '%s'
          AND dev.app_id = zmns.app_id
        GROUP BY dev.dev,
                 dev.app_id,
                 dev.channel,
                 dev.type,
                 zmns.ad_id,
                 zmns.ad_type,
                 zmns.type
        ) as b
        ON a.app_id=b.app_id AND a.ad_type = b.ad_type AND a.ad_id = b.ad_id
            ''' % (time, channel, time, channel)
    list = db.query(sql)

    if time < point:
        def func(x):
            x['dev_type'] = dev_type_filter(x.get('dev_type'))
            return x
        list = map(func, list)

    sum_install = 0
    sum_valid_install = 0
    for item in list:
        sum_install += item.get('install', 0)
        sum_valid_install += item.get('valid_install', 0)
    request_args = {
        'status': '',
        'platform_id': 3,
    }
    args = _setArgs(request_args)
    ad_lst = planList(args).get('data')
    # sql = "select id, title from advertisement"
    # ad_list = db.query(sql)
    ad_lst = {item.get('plan_id'): item.get('plan_name') for item in ad_lst}
    return render_template('plugin/clearing_detail.html',
                           query=list,
                           sum_install=sum_install,
                           sum_valid_install=sum_valid_install,
                           ad_lst=ad_lst,
                           time=time,
                           point=point)


@ad_plugin.route('/plugin/ad_clearing_detail')
@login_required
def ad_clearing_detail():
    ad_id = request.args.get('ad_id', '')
    time = request.args.get('time')

    sql = '''
        SELECT
            ns.channel,
            dev.dev,
            ns.dev_id,
            dev.type,
            plg.active_new,
            SUM (ns.install) AS install,
            SUM (da.install) AS valid_install,
            adv.id,
            adv.title,
            adv.type as adv_type
        FROM
            daily_data_ns AS ns,
            plgin_data AS plg,
            developer AS dev,
            daily_data_detail AS da,
            advertisement AS adv
        WHERE
            ns.ad_id = '%s'
        AND ns.time = '%s'
        AND ns.install != 0
        AND ns.dev_id = plg.dev_id
        AND ns.time = plg.time
        AND dev.id = ns.dev_id
        AND da.dailydata_id = ns.id
        AND adv.id = '%s'
        GROUP BY
            ns.channel,
            dev.dev,
            dev.type,
            plg.active_new,
            ns.dev_id,
            adv.id,
            adv.title,
            adv.type
            ''' % (ad_id, time, ad_id)

    list = db.query(sql)

    sum_install = 0
    sum_valid_install = 0
    for item in list:
        sum_install += item.get('install', 0)
        sum_valid_install += item.get('valid_install', 0)

    # sql = "select id, dev from developer"
    # dev_list = db.query(sql)
    # dev_list = {item.get('id'): item.get('dev') for item in dev_list}

    return render_template('plugin/ad_clearing_detail.html',
                           dev_list=dev_list,
                           query=list,
                           sum_install=sum_install,
                           sum_valid_install=sum_valid_install)


@ad_plugin.route('/plugin/ad_clearing', methods=['GET', 'POST'])
@login_required
def ad_clearing():
    ad_id = request.args.get('ad_id') or ''
    ad_name = request.args.get('ad_name') or ''
    bd_id = request.args.get('bd_id') or ''
    sdate = request.args.get('sdate') or g.now
    edate = request.args.get('edate') or g.now
    day = int(request.args.get('day') or 0)
    try:
        sdate_before = StrToDate(sdate, -1)
    except Exception:
        sdate_before = sdate - timedelta(days=1)

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)
        sdate_before = sdate - timedelta(days=1)
    # sql = "select sum(install) as install, ad_id, time " \
    #       "from daily_data " \
    #       "where time>='%s' and time<='%s' " \
    #       "group by ad_id, time " \
    #       "ORDER BY time" % (sdate, edate)
    # query = db.query(sql)
    #
    #
    # # 插入更新数据
    # for item in query:
    #     sql = "select * from ad_clearing where ad_id='%s' and time='%s'" % (item.ad_id, item.time)
    #     query2 = db.query(sql)
    #     if not query2:
    #         sql = "insert into ad_clearing (ad_id, install, time)" \
    #               "VALUES ('%s', '%s', '%s')" % (item.ad_id, item.install, item.time)
    #         db.execute(sql)
    #     else:
    #         if query2[0].install != item.install:
    #             sql = "update ad_clearing set install='%s' where time='%s' and ad_id='%s'" % (
    #                 item.install, item.time, item.ad_id)
    #             db.execute(sql)

    if request.method == 'POST':
        sql = "select * from ad_clearing WHERE time>='%s' and time<='%s' and install != 0 order by time" % (
            sdate, edate)
        query = db.query(sql)
        for item in query:
            earnings_pre = request.form.get(str(item.id), 0)
            sql = "update ad_clearing set earnings_pre='%s' where time = '%s' and ad_id = '%s'" \
                  % (earnings_pre, item.time, item.ad_id)
            db.execute(sql)
    # sql = "select a.*, b.title as ad " \
    #       "from ad_clearing as a, advertisement as b " \
    #       "WHERE a.time>='%s' and a.time<='%s' and a.ad_id=b.id and install != 0" % (sdate, edate)

    sql = '''
        SELECT a.*, b.title AS ad_name, b.w_id, SUM(c.click) AS click, SUM (d.install) AS valid_install
        FROM ad_clearing AS a,
             advertisement AS b,
             daily_data_ns AS c,
             daily_data_detail AS d
        WHERE a.time>='%s'
          AND a.time<='%s'
          AND a.time = c.time
          AND d.dailydata_id = c.id
          AND a.ad_id=b.id
          AND a.ad_id=c.ad_id
          AND b.state=(CASE WHEN a.install=0 THEN 1 ELSE @state END)
        ''' % (sdate_before, edate)

    sql += " and a.ad_id='%s'" % ad_id if ad_id else ''
    sql += " and b.title like '%s%s%s'" % ('%', ad_name, '%') if ad_name else ''
    sql += " and b.bd_id='%s'" % bd_id if bd_id else ''
    sql += " group by a.id, b.title, b.w_id, a.time order by time desc"
    query = db.query(sql)
    op_sql = "select id, data_before, data_after, op_data_id, data_type, time, timestamp " \
             "from operations " \
             "where data_type = 0 " \
             "order by time, timestamp"

    op_list = db.query(op_sql)
    # query_install = None
    # query_no_install = None
    query_online = []
    query_offline = []
    # 比较前一天的收入
    if query:
        for item in query:
            for item_b in query:
                if item['ad_id'] == item_b['ad_id'] and item['time'] - timedelta(days=1) == item_b['time']:
                    if item['earnings_install'] > item_b['earnings_install']:
                        item['cmp_earnings_install'] = 1
                    elif item['earnings_install'] < item_b['earnings_install']:
                        item['cmp_earnings_install'] = -1
                    else:
                        item['cmp_earnings_install'] = 0
                    break

            # 下线状态
            item['status'] = 1
            op_list_id = filter(lambda x: x.get('op_data_id') == item.get('ad_id'), op_list)
            if op_list_id:
                op_list_ago = filter(lambda x: x.get('time') <= item.get('time'), op_list_id)
                if op_list_ago:
                    op_list_ago = sorted(op_list_ago, key=lambda x: (x['time'], x['id']), reverse=True)
                    if op_list_ago[0]['data_after'] == '0':
                        item['status'] = 0

        query = filter(lambda x: x['time'] != sdate_before, query)
        query_online = filter(lambda x: x['status'] == 1, query)
        query_offline = filter(lambda x: x['status'] == 0, query)
        # query_install = filter(lambda x: x['install'] != 0, query)
        # query_no_install = filter(lambda x: x['install'] == 0, query)

    # 预收总计
    sum_pre = 0
    sum_earning = 0
    sum_click = 0
    sum_install = 0
    sum_valid_install = 0
    if query:
        for item in query:
            sum_pre += item['earnings_pre']
            sum_earning += item['earnings_install']
            sum_click += item['click']
            sum_install += item['install']
            sum_valid_install += item['valid_install']

            # 获取arpu_3
            sql = "select arpu_install from ad_clearing where ad_id='%s' and time>='%s' and time<='%s'" \
                  % (item.ad_id, item.time - datetime.timedelta(days=3), item.time)
            query3 = db.query(sql)
            arpu_3 = 0
            if query3:
                for item2 in query3:
                    arpu_3 += item2.arpu_install
                arpu_3 /= len(query3)
            item['arpu_3'] = arpu_3

    return render_template('plugin/ad_clearing.html',
                           query=query_online,
                           query_offline=query_offline,
                           sdate=sdate,
                           edate=edate,
                           ad_name=ad_name,
                           bd_id=bd_id,
                           sum_click=sum_click,
                           sum_install=sum_install,
                           sum_pre=sum_pre,
                           sum_earning=sum_earning,
                           sum_valid_install=sum_valid_install,
                           ad_id=ad_id,
                           bd_list=bd_filter)


@ad_plugin.route('/plugin/push_group', methods=['GET', 'POST'])
def push_group():
    if request.method == 'POST':
        ad_id = request.form.get('ad_id')
        if not ad_id:
            flash(u'请选择广告', 'error')
        sql = "select ad_id from specgroups where ad_id='%s'" % (ad_id)
        check = db.query(sql)
        if check:
            flash(u'广告已存在组中', 'error')
        else:
            sql = "insert into specgroups (ad_id) VALUES ('%s')" % (ad_id)
            db.execute(sql)
            flash(u'添加成功', 'success')

    sql = "select a.*, b.title from specgroups as a, advertisement as b where a.ad_id=b.id"
    query = db.query(sql)

    sql = "select id, title from advertisement"
    query2 = db.query(sql)

    return render_template('plugin/push_group.html',
                           list=query,
                           ad_list=query2)


@ad_plugin.route('/crm/push_group_del', methods=['GET', 'POST'])
def push_group_del():
    ad_id = request.form.get('id')
    sql = "delete from specgroups WHERE ad_id='%s'" % (ad_id)
    db.execute(sql)
    return json.dumps({'success': 1})


@ad_plugin.route('/crm/ad_clearing_add', methods=['GET', 'POST'])
def ad_clearing_add():
    sql = "select id,title from advertisement"
    ad_list = db.query(sql)
    if request.method == 'POST':
        ad_id = request.form.get('ad_id')
        date = request.form.get('date')
        money = request.form.get('money')

        sql = "insert into ad_clearing (ad_id, time, earnings_install) VALUES ('%s', '%s', '%s')" % (ad_id, date, money)
        db.execute(sql)
        flash('添加成功', 'success')
        return '''
        <script type="text/javascript">
            frameElement.api.opener.location.reload();
            frameElement.api.close();
        </script>
        '''

    return render_template('plugin/window.html',
                           ad_list=ad_list)


from ..utils.white_list import checkWhiteList, whiteAppend


@ad_plugin.route('/white_list', methods=['GET', 'POST'])
def white_list():
    app_id = request.args.get('app_id')
    channel = request.args.get('channel')
    type = request.args.get('type')
    ad_list = 'ad_lst' if type == '1' else 'black_ad_lst'

    if request.method == 'POST':
        ad_id = request.form.getlist('ad_id')
        if ad_id:
            for ad_id in ad_id:
                id = checkWhiteList(app_id)
                if ad_id:
                    state = whiteAppend(app_id, ad_id, type)
            if state == 0:
                flash('已存在')
            elif state == 1:
                flash('添加成功')
        else:
            flash('请选择广告！')

    sql = "select a.*, b.%s as ad_lst from developer as a, dev_whitelst as b where a.app_id=b.app_id and b.app_id='%s'" % (
        ad_list, app_id)
    query1 = db.query(sql)
    query1 = filterWhiteName(query1)

    sql = "select id, title from advertisement where state=1"
    query2 = db.query(sql)
    return render_template('plugin/white_list.html',
                           ad_list=query2,
                           channel=channel,
                           app_id=app_id,
                           query=query1,
                           type=type, )


@ad_plugin.route('/white_delete', methods=['GET', 'POST'])
def white_delete():
    ad_id = request.form.get('ad_id')
    app_id = request.form.get('app_id')
    type = request.form.get('type')
    ad_list = 'ad_lst' if type == '1' else 'black_ad_lst'

    sql = "update dev_whitelst set %s = array_remove(%s, '%s') where app_id='%s'" % (ad_list, ad_list, ad_id, app_id)
    ret = db.execute(sql)

    if ret:
        return json.dumps({'success': 1})
    else:
        return ''


@ad_plugin.route('/action_data', methods=['GET', 'POST'])
def action_data():
    channel = request.args.get('channel', '')
    sdate = request.args.get('sdate', g.now)
    edate = request.args.get('edate', g.now)
    day = int(request.args.get('day') or 0)
    page = int(request.args.get('page') or 1)
    duration1 = request.args.get('duration1') or '60'
    duration2 = request.args.get('duration2') or '120'
    duration3 = request.args.get('duration3') or '300'
    duration4 = request.args.get('duration4') or '600'
    duration5 = request.args.get('duration5') or '1800'

    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    sql = '''
        SELECT
            a.time,
            b.dev,
            b.channel,
            c.user_showad,
            c.active_new,
            count(a.duration) c0,
            count(CASE WHEN a.duration>= %s THEN 1 END) c1,
            count(CASE WHEN a.duration>= %s THEN 1 END) c2,
            count(CASE WHEN a.duration>= %s THEN 1 END) c3,
            count(CASE WHEN a.duration>= %s THEN 1 END) c4,
            count(CASE WHEN a.duration>= %s THEN 1 END) c5,
            count(*) over()
        FROM
            action_data AS a,
            developer AS b,
            plgin_data AS c
        WHERE
            a.app_id = b.app_id
          AND a.time>='%s'
          AND a.time<='%s'
          AND c.time>='%s'
          AND c.time<='%s'
          AND a.time = c.time
          AND c.dev_id = b.id
        ''' % (duration1, duration2, duration3, duration4, duration5, sdate, edate, sdate, edate)
    sql += " and b.channel=%s" % (channel) if channel else ''
    sql += ''' GROUP BY a.time, b.dev, b.channel, c.user_showad, c.active_new
                ORDER BY time DESC
                LIMIT 50 OFFSET 50* %s''' % (page - 1)
    query = db.query(sql)
    dict_args = {
        'channel': channel,
        'sdate': sdate,
        'edate': edate
    }
    args = setArgs(dict_args)
    pag = pagination.Pagination(query or [], page, 50, query[0].count if query else None)
    return render_template('plugin/action_data.html',
                           query=query,
                           sdate=sdate,
                           edate=edate,
                           channel=channel,
                           pagination=pag,
                           args=args,
                           duration1=round(float(duration1), 2),
                           duration2=round(float(duration2), 2),
                           duration3=round(float(duration3), 2),
                           duration4=round(float(duration4), 2),
                           duration5=round(float(duration5), 2))


@ad_plugin.route('/sdk_test', methods=['GET', 'POST'])
def sdk_test():
    app_id = request.args.get('app_id') or ''
    imei = request.args.get('imei') or ''
    clear = request.args.get('clear')
    search = request.args.get('search')

    query = []
    if clear:
        if imei:
            sql = "select id from phone_info where imei='%s'" % (imei)
            id = db.query(sql)
            id = id[0].get('id') if id else 0
            sql = "update phone_info_ad set adlst='{}', adlst_active='{}' where client_id='%s'" % (id)
            res = db.execute(sql)
            flash('清除成功！') if res else flash('清除失败，请检查imei是否正确')
        else:
            flash('请填写正确的imei！')
    elif search:
        if app_id:
            sql = "select app_id, count(case when action in (0, 100, 200, 300) then 1 end) as show, count(case when action in (1, 101, 201, 301) then 1 end)click, count(case when action in (2, 202) then 1 end)download, count(case when action in (3, 203) then 1 end)install " \
                  "from base_data where app_id='%s' and time='%s' " \
                  "group by app_id" % (app_id, g.now)
            query = db.query(sql)
        else:
            flash('请填写正确的应用id！')
    else:
        pass
    return render_template('/plugin/sdk_test.html',
                           app_id=app_id,
                           imei=imei,
                           query=query,
                           test_phone_imei=test_phone_imei)


from ..utils.filter import *


@ad_plugin.route('/ad_result')
def ad_result():
    ad_id = request.args.get('ad_id', '').replace(' ', '')
    ad_name = request.args.get('ad_name', '').replace(' ', '')
    w_title = request.args.get('w_title', '').replace(' ', '')
    sdate = request.args.get('sdate', g.before)
    edate = request.args.get('edate', g.before)
    day = int(request.args.get('day') or 0)
    if day:
        sdate = StrToDate(sdate, day)
        edate = StrToDate(edate, day)

    sql = "select a.*, b.title, b.w_title, b.target, b.charge_type, b.exemplar, b.bd_id, b.adv_price, b.state " \
          "from ad_result as a, advertisement as b " \
          "where a.ad_id=b.id and date>='%s' and date<='%s'" % (sdate, edate)
    if ad_id:
        sql += " and b.id='%s'" % (ad_id)
    if ad_name:
        sql += " and b.title like '%s%s%s'" % ('%', ad_name, '%')
    if w_title:
        sql += " and b.w_title like '%s%s%s'" % ('%', w_title, '%')
    sql += " order by a.date desc"

    list = db.query(sql)

    sql = "select data_before, data_after, op_data_id, data_type, time, timestamp " \
          "from operations " \
          "where data_type in (0, 1) " \
          "order by time, timestamp"
    op_list = db.query(sql)

    # 添加exemplar变更记录
    if list:
        for item in list:
            _op_list = filter(lambda x: x.get('op_data_id') == item.get('ad_id') and x.get('time') == item.get('date'),
                              op_list)
            if _op_list:
                for ex in _op_list:
                    if ex == _op_list[0]:
                        item['exe'] = []
                        item['exe'].append({'timestamp': '', 'exemplar': exemplar_filter(ex.get('data_before'))})
                    item['exe'].append(
                        {'timestamp': str(ex.get('timestamp')), 'exemplar': exemplar_filter(ex.get('data_after'))})
            else:
                bf_op_list = filter(
                    lambda x: x.get('op_data_id') == item.get('ad_id') and x.get('time') < item.get('date'),
                    op_list)
                if bf_op_list:
                    ex = bf_op_list[-1]
                    item['exe'] = []
                    item['exe'].append({'timestamp': '', 'exemplar': exemplar_filter(ex.get('data_after'))})
                else:
                    aft_op_list = filter(
                        lambda x: x.get('op_data_id') == item.get('ad_id') and x.get('time') > item.get('date'),
                        op_list)
                    if aft_op_list:
                        ex = aft_op_list[0]
                        item['exe'] = []
                        item['exe'].append({'timestamp': '', 'exemplar': exemplar_filter(ex.get('data_before'))})

            # 下线状态
            _op_list = filter(lambda x: x.get('op_data_id') == item.get('ad_id') and x.get('data_type') == 0, op_list)
            if _op_list:
                bf_op_list = filter(lambda x: x.get('time') <= item.get('date'), _op_list)
                if bf_op_list:
                    ex = bf_op_list[-1]
                    item['state'] = 0 if ex.get('data_after') == '0' else 1
                else:
                    aft_op_list = filter(lambda x: x.get('time') > item.get('date'), _op_list)
                    if aft_op_list:
                        ex = aft_op_list[0]
                        item['state'] = 0 if ex.get('data_before') == '0' else 1

    list = sorted(list, key=lambda x: x['state'], reverse=True)
    show = 1
    click = 1
    download = 1
    install = 1
    back_num = 0
    earning = 0
    pay = 0
    profit = 0
    active_new = {'total': 1}
    if list:
        for item in list:
            item.click_rate = item.click / float(item.show) * 100 if item.show else 0
            item.download_rate = item.download / float(item.show) * 100 if item.show else 0
            item.install_rate = item.install / float(item.download) * 100 if item.download else 0
            item.profit = item.earning - item.pay
            item.profit_rate = (item.earning - item.pay) / item.earning * 100 if item.earning else 0
            item.target_type = 'wauee' if '.uzham.' in item.target else 'cp'
            item.charge_type = charge_type_filter.get(item.charge_type)
            item.exemplar = exemplar_filter(item.exemplar)
            item.bd = bd_filter.get(item.bd_id)

            # 统计总数
            show += item.show
            click += item.click
            download += item.download
            install += item.install
            back_num += item.back_num
            earning += item.earning
            pay += item.pay
            profit += item.profit
            if not active_new.has_key(item.date):
                active_new.update({item.date: item.all_active_new, 'total': active_new['total'] + item.all_active_new})

    return render_template('/plugin/ad_result.html',
                           list=list,
                           ad_id=ad_id,
                           ad_name=ad_name,
                           w_title=w_title,
                           sdate=sdate,
                           edate=edate,
                           show=show,
                           click=click,
                           download=download,
                           install=install,
                           earning=earning,
                           pay=pay,
                           profit=profit,
                           back_num=back_num,
                           active_new=active_new.get('total'))


# ---------------------------------------
from ..models.api import PushToCrm


@ad_plugin.route('/push_crm', methods=['GET', 'POST'])
def push_crm():
    sdate = request.form.get('sdate', g.now)
    edate = request.form.get('edate', g.now)

    sql = "select a.earnings_pre as money, a.app_id, b.dev as app_name, a.time as date, a.id " \
          "from dev_clearing as a, developer as b " \
          "where a.app_id=b.app_id and a.time>='%s' and a.time<='%s'" % (sdate, edate)
    query = db.query(sql)
    query = filter(lambda a: a.get('app_name')[0] == 'F' and a.get('money') != 0, query)

    if query:
        for item in query:
            x = item.get('app_name').split('_')
            # item['user_id'] = x[1]
            item.update({"date": str(item.get('date'))})
            item.update({"money": str(item.get('money'))})
            item.update({"user_id": x[1]})

    args = json.dumps({'lst': query})
    try:
        res = PushToCrm(args)
    except Exception, e:
        logging.error(e)
        res = ''
    if res:
        status = json.loads(res).get('status')
        logging.warn(status)
    else:
        status = 0
    if status == 200:
        # 更改状态
        lst = ''
        if query:
            for item in query:
                lst += str(item.get('id')) if not lst else ',' + str(item.get('id'))
        sql = "update dev_clearing set state=1 where id in (%s)" % (lst)
        db.execute(sql)
        return jsonify(success=1)
    else:
        return ''


from ..utils.JudgeLink import JudgeLink


@ad_plugin.route('/plugin/judge_link', methods=['GET', 'POST'])
@login_required
def judge_link():
    link = request.form.get('link')
    judge_link = JudgeLink()
    res = judge_link.send_request(url=link)
    if res == 200:
        status = '1'
    else:
        status = ''
    return status


# ----------------api------------------------
@ad_plugin.route('/plugin_api/edit_dev_type', methods=['POST'])
def edit_dev_type():
    id = request.form.get('id', '')
    dev_type = request.form.get('dev_type', '')
    sql = "update developer set type=%s where id=%s" % (dev_type, id)
    s = db.execute(sql)
    status = 200 if s else 600
    return json.dumps({'status': status})


@ad_plugin.route('/plugin_api/dev_add', methods=['GET', 'POST'])
def dev_add():
    if request.method == 'POST':
        # 添加app_id和dev
        base = 10000
        dev = request.form.get('dev', '')
        user_id = request.form.get('user_id', '')
        if dev == '':
            status = 601
            return json.dumps({'status': status})

        dev = 'F_' + str(user_id) + '_' + str(dev)
        sql = "select dev from developer where dev='%s'" % (dev)
        query = db.query(sql)
        if query:
            status = 602
            return json.dumps({'status': status})

        app_id = uuid.uuid1()
        sql = "insert into developer (dev, app_id, user_id) VALUES ('%s', '%s', '%s')" % (dev, app_id, user_id)
        db.execute(sql)

        # 更新渠道号
        sql = "select id from developer where app_id='%s'" % (app_id)
        channel = db.query(sql)[0].id + base
        sql = "update developer set channel='%s' where app_id='%s'" % (channel, app_id)
        res = db.execute(sql)
        if res:
            status = 200
        else:
            status = 600
        return json.dumps({'status': status})


@ad_plugin.route('/plugin_api/dev_list', methods=['GET', 'POST'])
def dev_list():
    user_id = request.args.get('user_id', '')

    sql = "select * from developer where user_id='%s' and state!=2 order by id" % (user_id)
    query = db.query(sql)

    res = {
        'status': 200,
        'list': query,
    }
    return json.dumps(res)


# 开关操作记录
def op_record(channel, op_id='-1', switch='0'):
    sql = "insert into dev_operation (switch, channel, op_id) VALUES ('%s', '%s', '%s')" % (switch, channel, op_id)
    res = db.execute(sql)
    return res


@ad_plugin.route('/plugin/running_state', methods=['GET', 'POST'])
def running_state():
    channel = request.form.get('channel')
    running_state = request.form.get('running_state')
    s = request.form.get('s')
    op_id = request.form.get('op_id') or current_user.user_id

    if not s:
        sql = "update developer set switch='%s' where channel='%s'" % (running_state, channel)
        res = db.execute(sql)
        op_record(channel, op_id, running_state)
    else:
        sql = "update developer set state='%s' where channel='%s'" % (running_state, channel)
        res = db.execute(sql)

    if res:
        status = 200
    else:
        status = 600
    return json.dumps({'status': status})


@ad_plugin.route('/plugin/channel_delete', methods=['GET', 'POST'])
@login_required
def channel_delete():
    channel = request.form.get('channel')
    sql = "delete from developer WHERE channel='%s'" % (channel)
    # try:
    db.execute(sql)
    return json.dumps({'success': 1})


@ad_plugin.route('/plugin/change_adTime', methods=['GET', 'POST'])
def change_adTime():
    id = request.form.get('id', '')
    val = request.form.get('time', '')
    d = request.form.get('d', '')
    s = request.form.get('s', '')

    if s:
        sql = "update developer set sub_active_time='%s' where id='%s'" % (val, id)
    elif d:
        sql = "select dev from developer where dev='%s'" % (val)
        query = db.query(sql)
        if query:
            return json.dumps({'status': 601})
        else:
            sql = "update developer set dev='%s' where id='%s'" % (val, id)
    else:
        sql = "update developer set ad_launch_time='%s' where id='%s'" % (val, id)
    s = db.execute(sql)

    status = 200 if s else 600
    return json.dumps({'status': status})


# 从分发导入实收
import time


@ad_plugin.route('/plugin/data_push', methods=['GET', 'POST'])
@login_required
def data_push():
    sdate = request.form.get('sdate', g.before)
    edate = request.form.get('edate', g.before)

    from tm.util.sign import hexdigest_hash

    SECRET_KEY = "9157cab7-645f-4b35-8fa5-d5c9975defce"

    api_host = "http://api.wauee.com"
    request_args = {
        "t": int(time.time()),
        "secret_key": SECRET_KEY,
        "member_id": '56545',
        "start_order_date": sdate,
        "end_order_date": edate,
    }
    oauth_key = hexdigest_hash(pop_keys=["oauth_key"], **request_args)
    request_args.update({"oauth_key": oauth_key})
    request_args.pop("secret_key")
    uri = "commissions"
    request_url = "?".join(("/".join((api_host, uri)), urllib.urlencode(request_args)))
    res = requests.get(request_url)
    res = res.content
    list = json.loads(res).get('data')

    # 合并渠道号
    push_list = []
    if list:
        for item in list:
            if [item.get('product_id'), item.get('order_date')] not in [[x.get('product_id'), x.get('order_date')] for x
                                                                        in push_list]:
                item['cp_fee'] = reduce(lambda x, y: x + y, [x.get('feevalue') for x in filter(
                    lambda x: x.get('product_id') == item.get('product_id') and x.get('order_date') == item.get(
                        'order_date'), list)])
                item['cp_norder'] = reduce(lambda x, y: x + y, [x.get('norder') for x in filter(
                    lambda x: x.get('product_id') == item.get('product_id') and x.get('order_date') == item.get(
                        'order_date'), list)])
                push_list.append(item)

    # 累计导入个数
    num = 0
    for item in push_list:
        sql = "update ad_clearing set earnings_install='%s', arpu_install=%s/(case install when 0 then 1 else install end), back_num=%s, is_pull=1" \
              "from advertisement " \
              "where ad_clearing.ad_id = advertisement.id and advertisement.w_id='%s' and ad_clearing.time='%s'" \
              % (
                  item.get('cp_fee'), item.get('cp_fee'), item.get('cp_norder'), item.get('product_id'),
                  item.get('order_date'))
        s = db.execute(sql)
        if s:
            num += 1

    # #同步更新广告效果表
    # sql = '''select A.*, B.all_pay, C.all_install, D.all_active_new from
    #         (select a.ad_id, sum(a.show) as show, sum(a.click)click, sum(a.download)download, sum(a.install)install, a.time,
    #         b.w_id, c.earnings_install as earning, c.back_num
    #         from daily_data as a, advertisement as b, ad_clearing as c
    #         where a.ad_id=b.id and c.ad_id=b.id and c.time=a.time and a.time>='%s' and a.time<='%s'
    #         group by a.ad_id, a.time, c.earnings_install, c.back_num, b.w_id)A,
    #
    #         (select sum(earnings_pre)all_pay, time as time1
    #         from dev_clearing
    #         where time>='%s' and time<='%s'
    #         group by time1)B,
    #
    #         (select sum(install)all_install, time as time2
    #         from daily_data
    #         where time>='%s' and time<='%s'
    #         group by time2)C,
    #
    #         (select sum(active_new)all_active_new, time as time3
    #         from plgin_data
    #         group by time3)D
    #         where A.time=B.time1 and B.time1=C.time2 and C.time2=D.time3'''%(sdate, edate, sdate, edate, sdate, edate)
    # list = db.query(sql)
    #
    # for item in list:
    #     request_args = {
    #         "pid": item.get('w_id'),
    #         "page": 1,
    #         "per_page": 10000,
    #         "secret_key": SECRET_KEY,
    #         "t": int(time.time()),
    #         "fields": 'biz,ad_price',
    #     }
    #     oauth_key = hexdigest_hash(pop_keys=["oauth_key"], **request_args)
    #     request_args.update({"oauth_key": oauth_key})
    #     request_args.pop("secret_key")
    #     uri = "products"
    #     request_url = "?".join(("/".join((api_host, uri)), urllib.urlencode(request_args)))
    #     res = requests.get(request_url)
    #     res = res.content
    #     data = json.loads(res).get('data')
    #
    #     bd_id = data[0].get('biz') if data else 0
    #     ad_price = data[0].get('ad_price') if data else 0
    #     item.update({
    #         'bd_id': bd_id if bd_id else 0,
    #         'ad_price': ad_price if ad_price else 0,
    #         'pay': (float(item.all_pay) * item.install / item.all_install + float(item.earning) * 0.065) if item.all_install else 0,
    #     })
    #     item.update({
    #         'profit': float(item.earning) - item.pay,
    #         'ecpm': (item.earning / item.show * 1000) if item.show else 0,
    #         'arpu': (item.earning / item.install) if item.install else 0,
    #         'active_arpu': (item.earning / item.all_active_new) if item.all_active_new else 0,
    #     })
    #
    #
    #     sql = "select id from ad_result where ad_id=%s and date='%s'" %(item.ad_id, item.time)
    #     id = db.query(sql)
    #
    #     if id:
    #         sql = '''update ad_result set ad_price=%s, show=%s, click=%s, download=%s, install=%s, all_active_new=%s, back_num=%s,
    #                 earning=%s, pay=%s, ecpm=%s, arpu=%s, active_arpu=%s where id=%s''' \
    #               %(item.ad_price, item.show, item.click, item.download, item.install, item.all_active_new, item.back_num, item.earning, item.pay,
    #                 item.ecpm, item.arpu, item.active_arpu, id[0].get('id'))
    #     else:
    #         sql = '''insert into ad_result
    #                 (ad_id, bd_id, ad_price, show, click, download, install, all_active_new, back_num, earning, pay, ecpm, arpu, active_arpu, date)
    #                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s')'''\
    #               %(item.ad_id, item.bd_id, item.ad_price, item.show, item.click, item.download, item.install, item.all_active_new, item.back_num, item.earning, item.pay, item.ecpm, item.arpu, item.active_arpu, item.time)
    #     db.execute(sql)

    res = {
        'status': 200,
        'num': num,
    }
    return json.dumps(res)


@ad_plugin.route('/plugin/spell', methods=['GET', 'POST'])
def spell():
    spell = request.form.get('spell', '')

    sql = "select id, title from advertisement"
    if 'Z' >= spell >= 'A':
        sql += " where left(title_acronym, 1)='%s'" % (spell)
    elif spell == '#':
        sql += " where left(title_acronym, 1)>'Z' or left(title_acronym, 1)<'A'"
    query = db.query(sql)

    ret = {
        'status': 200,
        'list': query,
    }
    return json.dumps(ret)


g_ip_list = []
ip_record_path = 'app/record/ip_record.txt'


def get_ip_list():
    if not g_ip_list:
        f = file(ip_record_path)
        str = f.read()
        ip_list = str.split(',')
    else:
        ip_list = g_ip_list
    return ip_list


@ad_plugin.route('/plugin/ip_record', methods=['GET', 'POST'])
def ip_record():
    ip = request.args.get('ip') or ''

    ip_list = get_ip_list()
    if ip in ip_list:
        res = {'status': 600}
    else:
        f = file(ip_record_path, 'a')
        f.write(ip + ',')
        f.close()
        g_ip_list.append(ip)
        res = {'status': 200}
    return json.dumps(res)


# ------------------------------------------------------

@ad_plugin.route('/wtf', methods=['GET', 'POST'])
def wtf():
    from ..forms.testForm import testForm

    form = testForm(**{'name': 'love'})
    print form.validate(), form.errors
    if form.validate_on_submit():
        pass

    return render_template('/test.html',
                           form=form)
