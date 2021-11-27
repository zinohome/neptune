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
from core import dbengine
from sqlalchemy.engine.base import Engine

'''config'''
cfg = config.app_config

class TestDBEngine(object):

    def test_connect(self):
        engine = dbengine.DBEngine().connect()
        print(engine.__class__)
        #for item in dir(engine):
        #    print(item)
        assert isinstance(engine, Engine)
        assert engine.pool.size() == cfg['Connection_Config'].con_pool_size