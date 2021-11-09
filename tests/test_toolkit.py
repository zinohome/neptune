#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune
from sqlalchemy.engine.url import URL

from util import toolkit


class TestToolkit:
    test = '{"id":3,"name":"sdf"}'
    testl = '{"id":3,"name":"sdf","phone":"234243"},' \
            '{"id":3,"name":"sdf","phone":"234243"},' \
            '{"id":3,"name":"sdf","phone":"234243"}'
    teddd = '{\'name\': \'yourname\',\'phone\':\'241124\'}'

    def test_is_dict(self):
        teststr = "{'aa','ddd'}"
        testestr = "{aa,ddd}"
        assert toolkit.is_dict(teststr) == True
        assert toolkit.is_dict(testestr) == False

    def test_to_dict(self):
        teststr = "{'aa','ddd'}"
        assert type(toolkit.to_dict(teststr)) == set

    def test_is_json(self):
        teststr = '{"id":3,"name":"sdf"}'
        assert toolkit.is_json(teststr) == True

    def test_to_json(self):
        teststr = '{"id":3,"name":"sdf"}'
        print(toolkit.to_json(teststr))
        assert isinstance(toolkit.to_json(teststr),dict) == True

    def test_is_list(self):
        s_comma = 'one,two,three,four,five'
        print(toolkit.is_list(s_comma))
        assert toolkit.is_list(s_comma) == True

    def test_to_list(self):
        s_comma = 'one,two,three,four,five'
        print(toolkit.to_list(s_comma))
        assert type(toolkit.to_list(s_comma)) == list

    def test_is_fvcol(self):
        testl = '{"id":3,"name":"sdf","phone":"234243"},' \
                '{"id":3,"name":"sdf","phone":"234243"},' \
                '{"id":3,"name":"sdf","phone":"234243"}'
        assert toolkit.is_fvcol(testl) == True

    def test_to_fvcol(self):
        testl = '{"id":3,"name":"sdf","phone":"234243"},' \
                '{"id":3,"name":"sdf","phone":"234243"},' \
                '{"id":3,"name":"sdf","phone":"234243"}'
        print(type(toolkit.to_fvcol(testl)))
        assert type(toolkit.to_fvcol(testl)) == tuple

    def test_uappend(self):
        assert toolkit.uappend('id') == 'up_b_id'

    def test_uappendlist(self):
        assert toolkit.uappendlist(['id', 'name', 'phone']) == ['up_b_id', 'up_b_name', 'up_b_phone']

    def test_gen_dburi(self):
        print(str(toolkit.gen_dburi()))
        print(toolkit.gen_dburi())
        print(toolkit.gen_dburi().__class__)
        assert isinstance(toolkit.gen_dburi(),URL) == True
