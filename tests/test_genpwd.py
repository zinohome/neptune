#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune
from util import genpwd


class TestPwd:
    def test_verify_password(self):
        plain_password = 'passw0rd'
        hashed_password = genpwd.get_password_hash(plain_password)
        print('The hashed password of [ %s ] is [ %s ]' % (plain_password, hashed_password))
        print('Verify again: [ %s ]' % genpwd.verify_password(plain_password, hashed_password))
        assert genpwd.verify_password(plain_password, hashed_password)
