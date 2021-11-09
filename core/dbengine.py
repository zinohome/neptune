#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

from config import config
from sqlalchemy import create_engine
from util import toolkit, log
from urllib import parse


'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class DBEngine(object):
    def __init__(self):
        uri = ''
        if cfg.database['db_gendburi']:
            uri = str(toolkit.gen_dburi())
        else:
            olduri = cfg.database['db_uri']
            if 'UNQUOTEPASSWORD' in olduri:
                uri = olduri.replace("UNQUOTEPASSWORD", parse.unquote_plus(cfg.database['db_password']))
            else:
                uri = olduri
        log.logger.debug('Connect use uri [ %s ]' % uri)
        if cfg.database['db_dialect'] == 'oracle':
            self.__engine = create_engine(uri,
                                          echo=False,
                                          pool_size=cfg.connection['con_pool_size'],
                                          max_overflow=cfg.connection['con_max_overflow'],
                                          pool_use_lifo=cfg.connection['con_pool_use_lifo'],
                                          pool_pre_ping=cfg.connection['con_pool_pre_ping'],
                                          pool_recycle=cfg.connection['con_pool_recycle'],
                                          exclude_tablespaces=cfg.database['db_exclude_tablespaces'])
        else:
            self.__engine = create_engine(uri,
                                          echo=False,
                                          pool_size=cfg.connection['con_pool_size'],
                                          max_overflow=cfg.connection['con_max_overflow'],
                                          pool_use_lifo=cfg.connection['con_pool_use_lifo'],
                                          pool_pre_ping=cfg.connection['con_pool_pre_ping'],
                                          pool_recycle=cfg.connection['con_pool_recycle'])

    def connect(self):
        return self.__engine


if __name__ == '__main__':
    """
    engine = DBEngine().connect()
    print(engine.__class__)
    print(engine.pool.size())
    for item in dir(engine):
        print(item)
    """
