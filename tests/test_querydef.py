#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune
from config.querydef import QueryDef


class TestQuerydef:
    def test_query_def(self):
        print(QueryDef().custom_dict)
        assert isinstance(QueryDef().custom_dict, dict)
        print(QueryDef().getsql('testfunc2'))
        assert QueryDef().getsql('testfunc2') == 'select 10'
