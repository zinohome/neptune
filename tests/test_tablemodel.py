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
from util import log
from core import tablemodel
import json

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

class TestTableModel:
    def test_table_model(self):
        tm = tablemodel.TableModel('orders')
        '''
        log.logger.debug('test debug output [tm.name: %s]' % tm.name)
        log.logger.debug('test debug output [tm.fullname: %s]' % tm.fullname)
        log.logger.debug('test debug output [tm.dbmeta: %s]' % tm.dbmeta)
        log.logger.debug('test debug output [tm.use_schema: %s]' % tm.use_schema)
        log.logger.debug('test debug output [tm.schematable: %s]' % tm.schematable)
        log.logger.debug('test debug output [tm.exists: %s]' % tm.exists)
        log.logger.debug('test debug output [tm.realtable: %s]' % tm.realtable)
        log.logger.debug('test debug output [tm.columns: %s]' % tm.columns)
        log.logger.debug('test debug output [tm.columnvalues: %s]' % tm.columnvalues)
        log.logger.debug('test debug output [tm.primarykeys: %s]' % tm.primarykeys)
        log.logger.debug('test debug output [tm.primarykeyvalues: %s]' % tm.primarykeyvalues)
        log.logger.debug('test debug output [tm.has_column: %s]' % tm.has_column('orderDate'))
        log.logger.success('test debug output tm.select(): \n %s' % json.dumps(tm.select(), sort_keys=True, indent=4))
        
        log.logger.success('test debug output tm.select(): \n %s' % json.dumps(
            tm.select('*', None, None, 5, 20, None, None, False, False, False), sort_keys=True, indent=4))
        log.logger.success('test debug output tm.select(): \n %s' % json.dumps(
            tm.selectbyid('10123'), sort_keys=True, indent=4))
        log.logger.success('test debug output tm.select(): \n %s' % json.dumps(
            tm.selectbyid('112','customerNumber,orderDate','customerNumber'), sort_keys=True, indent=4))
        insertsql = '{"comments": "null","customerNumber": "103","orderDate": "2013-05-20","orderNumber": "10431",' \
                    '"requiredDate": "2013-05-29","shippedDate": "2013-05-22","status":"Shipped"}'
        '''
        insertsql = "{'comments': 'null','customerNumber': '103','orderDate': '2013-05-20','orderNumber': '10432','requiredDate': '2013-05-29','shippedDate': '2013-05-22','status':'Shipped'}"
        log.logger.success('test debug output tm.insert(): \n %s' % json.dumps(
            tm.insert('orderDate',insertsql), sort_keys=True, indent=4))
        log.logger.success('test debug output tm.select(): \n %s' % json.dumps(
            tm.selectbyid('10432'), sort_keys=True, indent=4))
        updatesql = "{'comments': 'null','customerNumber': '103','orderDate': '2021-05-20','orderNumber': '10432','requiredDate': '2013-05-29','shippedDate': '2013-05-22','status':'NoShipped'}"
        log.logger.success('test debug output tm.updatebyid(): \n %s' % json.dumps(
            tm.updatebyid('orderNumber', '10432', updatesql), sort_keys=True, indent=4))
        log.logger.success('test debug output tm.select(): \n %s' % json.dumps(
            tm.selectbyid('10432'), sort_keys=True, indent=4))
        log.logger.success('test debug output tm.deletebyid(): \n %s' % json.dumps(
            tm.deletebyid('orderNumber', '10432'), sort_keys=True, indent=4))
        assert tm.has_column('orderDate') == True
