#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound

from admin.apps.config import blueprint
from flask import Response
import json

from core import dbmeta
from config import config
from util import log,genpwd
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

@blueprint.route('/settings-config/savedata',  methods = ['POST', 'GET'])
@login_required
def configSaveData():
    if request.method == 'POST':
        result = request.form
        log.logger.debug(result)

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
    userslist =  list(users.Users().users.values()).copy()
    for useritem in userslist:
        useritem['hashed_password'] = ''
        useritem['password'] = ''
        useritem['password_repeat'] = ''
        useritem['oldname'] = useritem['username']
    rdata = {
        'data': userslist,
        'recordsFiltered': len(userslist),
        'recordsTotal': len(userslist),
        'draw': request.args.get('draw', type=int),
    }
    return rdata

@blueprint.route('/settings-users/postdata',  methods = ['POST'])
@login_required
def postusersdata():
    requstdict = request.form.to_dict()
    if not requstdict['password'] == requstdict['password_repeat']:
        return Response('{"status":500, "password must equal with password_repeat! "}', status=500)
    else:
        if (len(requstdict['password'].strip()) == 0) or (len(requstdict['password_repeat'].strip()) == 0):
            return Response('{"status":500, "password must input ! "}', status=500)
        else:
            if requstdict['username'] not in users.Users().users.keys():
                newuser={}
                newuser['username'] = requstdict['username']
                newuser['full_name'] = requstdict['full_name']
                newuser['email'] = requstdict['email']
                newuser['hashed_password'] = genpwd.get_password_hash(requstdict['password'])
                newuser['role'] = requstdict['role']
                newuser['disabled'] = requstdict['disabled']
                users.Users().users[newuser['username']] = newuser
                users.Users().writeback()
                users.Users().reload()
                return Response(json.dumps(requstdict), status=200)
            else:
                return Response('{"status":500, "User already exists ! "}', status=500)

@blueprint.route('/settings-users/deletedata',  methods = ['DELETE'])
@login_required
def deleteusersdata():
    requstdict = request.form.to_dict()
    if requstdict['username'] not in users.Users().users.keys():
        return Response('{"status":500, "User does not exists ! "}', status=500)
    else:
        users.Users().deluser(requstdict['username'])
        users.Users().writeback()
        users.Users().reload()
        return Response(json.dumps(requstdict), status=200)


@blueprint.route('/settings-users/putdata',  methods = ['PUT'])
@login_required
def putusersdata():
    requstdict = request.form.to_dict()
    if not requstdict['password'] == requstdict['password_repeat']:
        return Response('{"status":500, "password must equal with password_repeat! "}', status=500)
    else:
        if (len(requstdict['password'].strip()) == 0) or (len(requstdict['password_repeat'].strip()) == 0):
            newuser = {}
            newuser['username'] = requstdict['oldname']
            newuser['full_name'] = requstdict['full_name']
            newuser['email'] = requstdict['email']
            newuser['hashed_password'] = users.Users().users[newuser['username']]['hashed_password']
            newuser['role'] = requstdict['role']
            newuser['disabled'] = requstdict['disabled']
            users.Users().users[newuser['username']] = newuser
            users.Users().writeback()
            users.Users().reload()
            return Response(json.dumps(requstdict), status=200)
        else:
            if not (requstdict['username'] == requstdict['oldname']):
                return Response('{"status":500, "Can not change username ! "}', status=500)
            else:
                newuser={}
                newuser['username'] = requstdict['oldname']
                newuser['full_name'] = requstdict['full_name']
                newuser['email'] = requstdict['email']
                newuser['hashed_password'] = genpwd.get_password_hash(requstdict['password'])
                newuser['role'] = requstdict['role']
                newuser['disabled'] = requstdict['disabled']
                users.Users().users[newuser['username']] = newuser
                users.Users().writeback()
                users.Users().reload()
                return Response(json.dumps(requstdict), status=200)