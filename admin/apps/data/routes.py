#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from admin.apps.data import blueprint

from core import dbmeta
from util import restclient

@blueprint.route('/data-view-<viewname>.html')
@login_required
def dataview(viewname):
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    # get data
    nc = restclient.NeptuneClient('admin', 'admin')
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        data = nc.toDataFrame(nc.fetch(viewname, '_table'), 'data').to_html(index=False, table_id="datatable",
                                                                            classes="table table-bordered table-striped")
    return render_template('home/data-view.html', segment='data-view-'+viewname, systables=systables, sysviews=sysviews, elename=viewname, data=data)

@blueprint.route('/data-table-<tablename>.html')
@login_required
def datatable(tablename):
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    # get data
    nc = restclient.NeptuneClient('admin', 'admin')
    if nc.token_expired:
        nc.renew_token()
    if (not nc.token_expired) and (nc.access_token is not None):
        data = nc.toDataFrame(nc.fetch(tablename, '_table'), 'data').to_html(index=False, table_id="datatable",
                                                                            classes="table table-bordered table-striped")
    return render_template('home/data-table.html', segment='data-table-'+tablename, systables=systables, sysviews=sysviews, elename=tablename, data=data)

