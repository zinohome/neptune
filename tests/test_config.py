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


class TestConfig:
    def test_config(self):
        cfg = config.app_config
        print(cfg['Application_Config'].app_description)
        print(cfg['Schema_Config'].schema_fetch_tables)
        print(cfg['Database_Config'].db_uri)
        assert cfg['Application_Config'].app_name == 'Neptune'
        assert cfg['Connection_Config'].con_max_overflow == 5

