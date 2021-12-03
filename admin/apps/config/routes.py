#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound

from admin.apps.config import blueprint

from core import dbmeta
from config import config
from util import log
from auth import users

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)


@blueprint.route('/settings-config.html',  methods = ['GET', 'POST'])
@login_required
def config():
    try:
        sysdbmeta = dbmeta.DBMeta()
        systables = sysdbmeta.get_tables()
        sysviews = sysdbmeta.get_views()
        confignamelist = list(cfg.keys())
        cfgjson = {}
        for cfgname in confignamelist:
           cfgijson = {}
           for item in cfg[cfgname].__dict__:
               if not item.startswith('_'):
                   cfgijson[item] = cfg[cfgname].__dict__[item]
           cfgjson[cfgname] = cfgijson
        return render_template('home/settings-config.html', segment='settings-config', systables=systables, sysviews=sysviews, confignamelist=confignamelist, cfgjson=cfgjson)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except Exception as exp:
        log.logger.error('Exception at route config() %s ' % exp)
        return render_template('home/page-500.html'), 500

@blueprint.route('/settings-users.html',  methods = ['GET', 'POST'])
@login_required
def userstable():
    try:
        sysdbmeta = dbmeta.DBMeta()
        systables = sysdbmeta.get_tables()
        sysviews = sysdbmeta.get_views()
        userskeylist = list(list(users.Users().users.values())[0].keys())
        return render_template('home/settings-users.html', segment='settings-users',
                           systables=systables, sysviews=sysviews, userskeylist=userskeylist)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500

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