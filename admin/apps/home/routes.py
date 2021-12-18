# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from admin.apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from auth import users
from config import config
from util import log
from core import dbmeta, dbengine


'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

@blueprint.route('/index')
@login_required
def index():
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    usercount = len(list(users.Users().users.values()))
    cpsize = 0
    cpchin = 0
    if cfg['Database_Config'].db_dialect == 'sqlite':
        cpsize = 1
        cpchin = 1
    else:
        cpsize = dbengine.DBEngine().connect().pool.size()
        cpchin=dbengine.DBEngine().connect().pool.checkedin()
    return render_template('home/index.html', segment='index', systables=systables, sysviews=sysviews,
                           usercount=usercount, cpsize=cpsize, cpchin=cpchin)

@blueprint.route('/index.html')
@login_required
def indexhtml():
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    usercount = len(list(users.Users().users.values()))
    cpsize = 0
    cpchin = 0
    if cfg['Database_Config'].db_dialect == 'sqlite':
        cpsize = 1
        cpchin = 1
    else:
        cpsize = dbengine.DBEngine().connect().pool.size()
        cpchin=dbengine.DBEngine().connect().pool.checkedin()
    return render_template('home/index.html', segment='index', systables=systables, sysviews=sysviews,
                           usercount=usercount, cpsize=cpsize, cpchin=cpchin)
@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:
        excludelist = ['settings-config', 'settings-users']
        if not template in excludelist:
            if not template.endswith('.html'):
                template += '.html'

            # Detect the current page
            segment = get_segment(request)
            sysdbmeta = dbmeta.DBMeta()
            systables = sysdbmeta.get_tables()
            sysviews = sysdbmeta.get_views()
            # Serve the file (if exists) from app/templates/home/FILE.html
            return render_template("home/" + template, segment=segment, systables=systables, sysviews=sysviews)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
