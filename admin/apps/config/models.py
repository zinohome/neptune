#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import config as apiconfig
from util import log
from flask_login import UserMixin



class SYSConfig(UserMixin):
    '''logging'''
    log = log.Logger(level=apiconfig.Config().application['app_log_level'])

    def __init__(self):
        self.api_config = apiconfig.Config()
        log.logger.debug(self.api_config)


if __name__ == '__main__':
    apcfg = SYSConfig()