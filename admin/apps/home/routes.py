# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from admin.apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound

from core import dbmeta


@blueprint.route('/index')
@login_required
def index():
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    return render_template('home/index.html', segment='index', systables=systables, sysviews=sysviews)

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
