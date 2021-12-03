#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_login import login_required
from admin.apps.config import blueprint

from core import dbmeta
from config import config
from util import log
from auth import users

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)


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
    log.logger.debug(users.Users().users)
    userslist = list(users.Users().users.values())
    userskeylist = list(list(users.Users().users.values())[0].keys())
    log.logger.debug(userslist)
    log.logger.debug(userskeylist)
    log.logger.debug(systables)
    return render_template('home/settings-users.html', userslist=userslist, userskeylist=userskeylist)

@blueprint.route('/settings-users/getdata',  methods = ['GET', 'POST'])
@login_required
def getusersdata():
    userslist = list(users.Users().users.values())
    rdata = {
        'data': userslist,
        'recordsFiltered': len(userslist),
        'recordsTotal': len(userslist),
        'draw': request.args.get('draw', type=int),
    }
    log.logger.debug(rdata)
    return rdata