#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

from core import dbmeta
from config import config
from util import log

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

class TestDBMeta:
    def test_load_metadata(self):
        meta = dbmeta.DBMeta()
        metadata = meta.metadata
        log.logger.debug("****************************************************")
        if metadata is not None:
            for item in dir(metadata):
                log.logger.debug(item)
            log.logger.debug("===================================================")
            for table in metadata.sorted_tables:
                log.logger.debug(table.name)
        log.logger.debug("****************************************************")
        log.logger.debug(meta.schema_file)
        assert True
