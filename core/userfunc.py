#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

import sys
import traceback
from fastapi.encoders import jsonable_encoder
from core import dbengine
from config import config
from util import log, toolkit
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker, scoped_session

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)


class UserFunc(object):
    def __init__(self, func_name):
        """Initialise the table from database schema."""
        self.funcname = func_name
        self.engine = dbengine.DBEngine().connect()

    def query(self, sqlstr, sqlparam):
        log.logger.debug('UserFunc query():')
        log.logger.debug('sqlstr: %s' % sqlstr)
        log.logger.debug('sqlparam: %s' % sqlparam)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            sql = text(sqlstr)
            log.logger.debug('SQL of Query: [ %s ]' % sql)
            param = toolkit.to_dict(sqlparam)
            result = session.execute(sql, param)
            d, a = {}, []
            if result is not None:
                log.logger.debug('Select Result: [ %s ]' % result)
                log.logger.debug('Select Result Return : [ %s ] rows ' % result.rowcount)
                for row in result:
                    # result.items() returns an array like [(key0, value0), (key1, value1)]
                    for column, value in row._mapping.items():
                        # build up the dictionary
                        d = {**d, **{column: value}}
                    a.append(d)
                return_json['data'] = a
            else:
                return_json['data'] = None
        except Exception as e:
            log.logger.error('Exception at userfunc query(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['updateResult'] = 'Error'
            return_json['updateError'] = 'Exception at userfunc query(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)


if __name__ == '__main__':
    uf = UserFunc('orders')
    json = uf.query('select * from orders where orderNumber > :id limit 10', {'id': 10000})
    log.logger.debug(json)
