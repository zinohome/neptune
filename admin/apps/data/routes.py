#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from admin.apps.data import blueprint

from core import dbmeta

@blueprint.route('/data-view-<viewname>.html')
@login_required
def dataview(viewname):
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    return render_template('home/data-view.html', segment='data-view-'+viewname, systables=systables, sysviews=sysviews)

@blueprint.route('/data-table-<tablename>.html')
@login_required
def datatable(tablename):
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    return render_template('home/data-table.html', segment='data-table-'+tablename, systables=systables, sysviews=sysviews)

