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
        cfg = config.Config()
        print(cfg.application.__class__)
        assert isinstance(cfg.application, dict)
        print(cfg.application['app_name'])
        assert cfg.application['app_name'] == 'Neptune'
        assert cfg.connection['con_max_overflow'] == 5

