#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import loguru
from flask import render_template, request, session
from flask_login import login_required
from jinja2 import TemplateNotFound
from admin.apps.data import blueprint

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
                           systables=systables, sysviews=sysviews, elename=viewname, meta=ncmeta)

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
        ncdata = nc.fetch(viewname, '_table', 'list', None, request.args.get('start', type=int),
                          request.args.get('length', type=int), True)
        rdata = {
            'data': ncdata['data'],
            'recordsFiltered': ncdata['record_count'],
            'recordsTotal': ncdata['record_count'],
            'draw': request.args.get('draw', type=int),
        }
    return rdata

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
                           systables=systables, sysviews=sysviews, elename=tablename, meta=ncmeta)

@blueprint.route('/data-table-<tablename>/getdata',  methods = ['GET', 'POST'])
@login_required
def gettabledata(tablename):
    # get data
    nc = restclient.NeptuneClient(session['username'],
                                  cryptutil.decrypt(cfg['Admin_Config'].SECRET_KEY, session['password']))
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        ncdata = nc.fetch(tablename, '_table', 'list', None, request.args.get('start', type=int),
                          request.args.get('length', type=int), True)
        rdata = {
            'data': ncdata['data'],
            'recordsFiltered': ncdata['record_count'],
            'recordsTotal': ncdata['record_count'],
            'draw': request.args.get('draw', type=int),
        }
    return rdata

@blueprint.route('/data-table-<tablename>/putdata',  methods = ['PUT'])
@login_required
def puttabledata(tablename):
    log.logger.debug(tablename)
    log.logger.debug(request)
    log.logger.debug(dir(request))
    log.logger.debug(request.method)
    log.logger.debug(request.form)

@blueprint.route('/data-table-<tablename>/deletedata',  methods = ['DELETE'])
@login_required
def deletetabledata(tablename):
    log.logger.debug(tablename)
    log.logger.debug(request)
    log.logger.debug(request.method)
    log.logger.debug(request.form)

@blueprint.route('/data-table-<tablename>/postdata',  methods = ['POST'])
@login_required
def posttabledata(tablename):
    log.logger.debug(tablename)
    log.logger.debug(request)
    log.logger.debug(request.method)
    log.logger.debug(request.form)
