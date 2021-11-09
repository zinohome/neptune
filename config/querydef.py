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
import config_with_yaml as config


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class QueryDef(object):
    def __init__(self):
        config_dir = os.path.dirname(os.path.abspath(__file__))
        cfg = config.load(os.path.join(config_dir, 'custom-query.yml'))
        self.custom_dict = cfg._config

    def getsql(self, funcname):
        rsql = None
        if funcname in self.custom_dict:
            func = self.custom_dict[funcname]
            rsql = func['func_sql']
        return rsql


if __name__ == '__main__':
    '''
    print(QueryDef().custom_dict)
    print(len(QueryDef().custom_dict))
    for func in QueryDef().custom_dict:
        print(func)
        print(QueryDef().custom_dict[func])
    print(QueryDef().getsql('testfunc2'))
    '''
