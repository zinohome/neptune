#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from flask import render_template, request, session
from flask_login import login_required

from admin.apps.authentication.forms import LoginForm
from admin.apps.data import blueprint
from flask import Response

from core import dbmeta
from util import restclient, cryptutil

from config import config
from util import log

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)


@blueprint.route('/data-view-<viewname>.html',  methods = ['GET', 'POST'])
@login_required
def dataview(viewname):
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    # get data
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        ncmeta = nc.fetch(viewname, '_schema/_table')
        return render_template('home/data-view.html', segment='data-view-'+viewname,
                           systables=systables, sysviews=sysviews, elename=viewname, meta=ncmeta['body'])
    else:
        return render_template('accounts/login.html', msg='Login time expired !', form=LoginForm())

@blueprint.route('/data-view-<viewname>/getdata',  methods = ['GET', 'POST'])
@login_required
def getviewdata(viewname):
    # get data
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        # ncmeta = nc.fetch(viewname, '_schema/_table')
        ncdata = nc.fetch(viewname, '_table', None, request.args.get('start', type=int),
                          request.args.get('length', type=int), True)
        rdata = {
            'data': ncdata['body']['data'],
            'recordsFiltered': ncdata['body']['record_count'],
            'recordsTotal': ncdata['body']['record_count'],
            'draw': request.args.get('draw', type=int),
        }
        log.logger.debug(rdata)
        return rdata
    else:
        return render_template('accounts/login.html', msg='Login time expired !', form=LoginForm())


@blueprint.route('/data-table-<tablename>.html', methods = ['GET', 'POST'])
@login_required
def datatable(tablename):
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    # get data
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        ncmeta = nc.fetch(tablename, '_schema/_table')
        return render_template('home/data-table.html', segment='data-table-'+tablename,
                           systables=systables, sysviews=sysviews, elename=tablename, meta=ncmeta['body'])
    else:
        return render_template('accounts/login.html', msg='Login time expired !', form=LoginForm())

@blueprint.route('/data-table-<tablename>/getdata',  methods = ['GET', 'POST'])
@login_required
def gettabledata(tablename):
    # get data
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        ncdata = nc.fetch(tablename, '_table', None, request.args.get('start', type=int),
                          request.args.get('length', type=int), True)
        rdata = {
            'data': ncdata['body']['data'],
            'recordsFiltered': ncdata['body']['record_count'],
            'recordsTotal': ncdata['body']['record_count'],
            'draw': request.args.get('draw', type=int),
        }
        return rdata
    else:
        return render_template('accounts/login.html', msg='Login time expired !', form=LoginForm())



@blueprint.route('/data-table-<tablename>/postdata',  methods = ['POST'])
@login_required
def posttabledata(tablename):
    requstdict = request.form.to_dict()
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        restbody = json.dumps({"fieldvalue":str(requstdict)})
        ncdata = nc.post(tablename, '_table', restbody)
        if ncdata['code'] == 200 and "insertResult" in ncdata['body'] and ncdata['body']['insertResult'] == 'True':
            return Response(json.dumps(requstdict), status=200)
        else:
            return Response('{"status":500, "body": "' + str(ncdata['body']) + '"}', status=500)
    else:
        return Response('{"status":500, "body": "{\"post error\":\"Login expired\"}"}', status=500)



@blueprint.route('/data-table-<tablename>/putdata',  methods = ['PUT'])
@login_required
def puttabledata(tablename):
    requstdict = request.form.to_dict()
    sysdbmeta = dbmeta.DBMeta()
    pkname = None
    idvalue = None
    pks = sysdbmeta.get_table_primary_keys(tablename)
    #TODO add multikey
    if len(pks) == 1:
        pkname = pks[0]
    if pkname is not None:
        idvalue = requstdict[pkname]
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        restbody = json.dumps({"fieldvalue":str(requstdict)})
        ncdata = nc.put(tablename, '_table', restbody, pkname, str(idvalue))
        if ncdata['code'] == 200 and "udpate_rowcount" in ncdata['body'] and int(ncdata['body']['udpate_rowcount']) > 0:
            return Response(json.dumps(requstdict), status=200)
        else:
            return Response('{"status":500, "body": "' + str(ncdata['body']) + '"}', status=500)
    else:
        return Response('{"status":500, "body": "{\"put error\":\"Login expired\"}"}', status=500)


@blueprint.route('/data-table-<tablename>/deletedata',  methods = ['DELETE'])
@login_required
def deletetabledata(tablename):
    requstdict = request.form.to_dict()
    sysdbmeta = dbmeta.DBMeta()
    pkname = None
    idvalue = None
    pks = sysdbmeta.get_table_primary_keys(tablename)
    #TODO add multikey
    if len(pks) == 1:
        pkname = pks[0]
    if pkname is not None:
        idvalue = requstdict[pkname]
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        ncdata = nc.deletebyid(tablename, '_table', pkname, str(idvalue))
        if ncdata['code'] == 200 and "delet_rowcount" in ncdata['body'] and ncdata['body']['delet_rowcount'] == 1:
            return Response('{"status":200, "body": "'+ str(ncdata['body'])+'"}', status=200)
        else:
            return Response('{"status":500, "body": "'+ str(ncdata['body'])+'"}', status=500)
    else:
        return Response('{"status":500, "body": "{\"delete error\":\"Login expired\"}"}', status=500)


