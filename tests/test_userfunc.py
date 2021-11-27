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
from core import userfunc

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

class TestUserFunc:
    def test_user_func(self):
        uf = userfunc.UserFunc('orders')
        json = uf.query('select * from orders where orderNumber > :id limit 10', {'id': 10000})
        log.logger.debug(json)
        assert True
