#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template, request, redirect
from flask_login import login_required
from jinja2 import TemplateNotFound

from admin.apps.config import blueprint
from flask import Response
import json
import configparser
from unipath import Path
import os

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
def settingsconfig():
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
        config_file = os.path.join(Path(os.path.abspath(__file__)).ancestor(4), 'config/settings.ini')
        rconfig = configparser.RawConfigParser()
        rconfig.optionxform = str
        rconfig.read(config_file)
        cfgini = {}
        for key in rconfig['settings']:
            cfgini[key] = rconfig['settings'][key]
        return render_template('home/settings-config.html', segment='settings-config', systables=systables, sysviews=sysviews, confignamelist=confignamelist, cfgjson=cfgjson, cfgini=cfgini)
    except TemplateNotFound:
        return render_template('home/page-404.html'), 404
    except Exception as exp:
        log.logger.error('Exception at route config() %s ' % exp)
        return render_template('home/page-500.html'), 500

@blueprint.route('/settings-config/savedata',  methods = ['POST', 'GET'])
@login_required
def configSaveData():
    if request.method == 'POST':
        submitdict = request.form.copy()
        dict_Application_Config = {}
        dict_Application_Config['app_name'] = cfg['Application_Config'].app_name
        dict_Application_Config['app_version'] = cfg['Application_Config'].app_version
        dict_Application_Config['app_description'] = cfg['Application_Config'].app_description
        dict_Application_Config['app_param_prefix'] = cfg['Application_Config'].app_param_prefix
        dict_Security_Config = {}
        dict_Security_Config['security_key'] = submitdict['security_key']
        dict_Security_Config['security_algorithm'] = submitdict['security_algorithm']
        dict_Security_Config['access_token_expire_minutes'] = submitdict['access_token_expire_minutes']
        dict_Admin_Config = {}
        dict_Admin_Config['DEBUG'] = submitdict['DEBUG']
        dict_Admin_Config['SECRET_KEY'] = submitdict['SECRET_KEY']
        dict_Admin_Config['SESSION_COOKIE_HTTPONLY'] = submitdict['SESSION_COOKIE_HTTPONLY']
        dict_Admin_Config['REMEMBER_COOKIE_HTTPONLY'] = submitdict['REMEMBER_COOKIE_HTTPONLY']
        dict_Admin_Config['REMEMBER_COOKIE_DURATION'] = submitdict['REMEMBER_COOKIE_DURATION']
        dict_Schema_Config = {}
        dict_Query_Config = {}
        dict_Database_Config = {}
        dict_Connection_Config = {}
        for key in submitdict.keys():
            if key.startswith('app_'):
                dict_Application_Config[key] = submitdict[key]
            if key.startswith('schema_'):
                dict_Schema_Config[key] = submitdict[key]
            if key.startswith('query_'):
                dict_Query_Config[key] = submitdict[key]
            if key.startswith('db_'):
                dict_Database_Config[key] = submitdict[key]
            if key.startswith('con_'):
                dict_Connection_Config[key] = submitdict[key]
        config_file = os.path.join(Path(os.path.abspath(__file__)).ancestor(4),'config/settings.ini')
        wconfig = configparser.RawConfigParser()
        wconfig.optionxform = str
        wconfig.add_section('settings')
        wconfig.set('settings', ';application settings', '')
        for key in dict_Application_Config:
            wconfig.set('settings', key, dict_Application_Config[key])
        wconfig.set('settings', ';schema settings', '')
        for key in dict_Schema_Config:
            wconfig.set('settings', key, dict_Schema_Config[key])
        wconfig.set('settings', ';query settings', '')
        for key in dict_Query_Config:
            wconfig.set('settings', key, dict_Query_Config[key])
        wconfig.set('settings', ';security settings', '')
        for key in dict_Security_Config:
            wconfig.set('settings', key, dict_Security_Config[key])
        wconfig.set('settings', ';database settings', '')
        for key in dict_Database_Config:
            wconfig.set('settings', key, dict_Database_Config[key])
        wconfig.set('settings', ';connection settings', '')
        for key in dict_Connection_Config:
            wconfig.set('settings', key, dict_Connection_Config[key])
        wconfig.set('settings', ';admin settings', '')
        for key in dict_Admin_Config:
            wconfig.set('settings', key.upper(), dict_Admin_Config[key])
        o = open(config_file, 'w')
        wconfig.write(o)
        o.close()
        return redirect(request.referrer)

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