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
import json
from util import log
from config import config

'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class Users(object):
    def __init__(self):
        auth_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(auth_dir, 'users.json'), 'r') as usersfile:
                self.users = json.loads(usersfile.read())
        except Exception as err:
            log.logger.error('Exception load Users file %s ' % err)


if __name__ == '__main__':
    '''
    print(Users().users)
    '''
