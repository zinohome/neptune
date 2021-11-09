#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

import os
from loguru import logger

LOG_FILE_NAME = 'neptune.log'


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Logger(object):
    def __init__(self, level='INFO'):
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        log_path = os.path.join(base_dir, 'log')
        # logger.add(sys.stderr, format="{time} {level} {message}", level=level)
        logger.add(os.path.join(log_path, LOG_FILE_NAME),
                   format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
                   rotation="100 MB",
                   retention="14 days",
                   level=level,
                   enqueue=True)
        self.logger = logger


if __name__ == '__main__':
    '''
    log = Logger(level='DEBUG')
    log.logger.success('[测试log] hello, world')
    log.logger.info('[测试log] hello, world')
    log.logger.debug('[测试log] hello, world')
    log.logger.warning('[测试log] hello, world')
    log.logger.error('[测试log] hello, world')
    log.logger.critical('[测试log] hello, world')
    log.logger.exception('[测试log] hello, world')
    '''
