#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

import ast
import re
from urllib import parse
import simplejson as json
from sqlalchemy.engine.url import URL
from config import config
from util import log

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)


def is_dict(dictstr):
    if isinstance(dictstr, dict):
        return True
    else:
        try:
            ast.literal_eval(dictstr)
        except ValueError:
            return False
        return True


def to_dict(dictstr):
    if isinstance(dictstr, dict):
        return dictstr
    elif is_dict(dictstr):
        return ast.literal_eval(dictstr)
    else:
        return None


def is_json(jsonstr):
    try:
        json.loads(jsonstr)
    except ValueError:
        return False
    return True


def to_json(jsonstr):
    if is_json(jsonstr):
        return json.loads(jsonstr)
    else:
        return None


def is_list(lststr):
    try:
        re.split(r'[\s\,\;]+', lststr)
    except TypeError:
        return False
    return True


def to_list(lststr):
    if is_list(lststr):
        return re.split(r'[\s\,\;]+', lststr)
    else:
        return [lststr]


def is_fvcol(lststr):
    try:
        ast.literal_eval(lststr)
    except SyntaxError:
        return False
    return True


def to_fvcol(lststr):
    if is_fvcol(lststr):
        return ast.literal_eval(lststr)
    else:
        return None

def convertSQLObject(vol, tableschema):
    log.logger.debug("====================================convertSQLObject====================================")
    log.logger.debug(vol)
    log.logger.debug(tableschema)


def uappend(lststr):
    return config.app_config['Application_Config'].app_param_prefix+'{}'.format(lststr)


def uappendlist(slist):
    return list(map(uappend, slist))


def gen_dburi():
    db = {'drivername': cfg['Database_Config'].db_drivername,
          'username': cfg['Database_Config'].db_username,
          'password': parse.unquote_plus(cfg['Database_Config'].db_password),
          'host': cfg['Database_Config'].db_host,
          'port': cfg['Database_Config'].db_port,
          'database': cfg['Database_Config'].db_name
          }
    return URL.create(**db)


if __name__ == '__main__':
    str1 = "{'name': 'productDescription', 'type': TEXT(), 'default': None, 'comment': None, 'nullable': False}"
    print(to_json(str1))

    print(uappendlist(['id', 'name', 'phone']))

    print(uappend('id'))
    print(gen_dburi().__class__)
    '''
    test = '{"id":3,"name":"sdf"}'
    testl = '{"id":3,"name":"sdf","phone":"234243"},' \
            '{"id":3,"name":"sdf","phone":"234243"},' \
            '{"id":3,"name":"sdf","phone":"234243"}'
    teddd = '{\'name\': \'yourname\',\'phone\':\'241124\'}'
    print(to_fvcol(teddd))
    print(to_fvcol(testl))
    pstr = [{'name': 'zhjjj'}, {'id': 12}, {'phone': '12345'}]
    fstr = 'name=:name and id = :id or phone =  :phone '
    print(str(gen_dburi()))
    print(gen_dburi().__class__)
    print(is_dict("{'aa','ddd'}"))
    print(is_dict("{aa,ddd}"))
    print(to_dict("{'aa','ddd'}"))
    print(type(to_dict("{'aa','ddd'}")))
    print(isinstance("{'id':3,'name':'sdf'}", dict))
    print(is_json(test))
    print(to_json(test).__class__)
    s_comma = 'one,two,three,four,five'
    print(is_list(s_comma ))
    print(type(to_list(s_comma)))
    '''
