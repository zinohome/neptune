#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from admin.apps.config import blueprint

from core import dbmeta

@blueprint.route('/settings-config')
@login_required
def config():
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    return render_template('home/settings-config.html', segment='settings-config', systables=systables, sysviews=sysviews)

@blueprint.route('/settings-users')
@login_required
def users():
    sysdbmeta = dbmeta.DBMeta()
    systables = sysdbmeta.get_tables()
    sysviews = sysdbmeta.get_views()
    return render_template('home/settings-users.html', segment='settings-users', systables=systables, sysviews=sysviews)
