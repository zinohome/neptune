#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import config
from util import log
from flask_login import UserMixin



class SYSConfig(UserMixin):
    '''logging'''
    log = log.Logger(level=config.app_config['Application_Config'].app_log_level)

    def __init__(self):
        self.api_config = config.app_config
        log.logger.debug(self.api_config)


if __name__ == '__main__':
    apcfg = SYSConfig()