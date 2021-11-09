#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune
from util.log import Logger


class TestLogger:
    def test_logger(self):
        log = Logger(level='DEBUG')
        log.logger.success('[测试log] hello, world')
        log.logger.info('[测试log] hello, world')
        log.logger.debug('[测试log] hello, world')
        log.logger.warning('[测试log] hello, world')
        log.logger.error('[测试log] hello, world')
        log.logger.critical('[测试log] hello, world')
        log.logger.exception('[测试log] hello, world')
        assert True
