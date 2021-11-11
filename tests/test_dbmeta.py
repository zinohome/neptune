#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from core import dbmeta
from config import config
from util import log

'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])

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
