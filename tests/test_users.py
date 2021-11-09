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
from auth import users

class TestUsers:
    def test_users(self):
        print(users.Users().users)
        assert isinstance(users.Users().users, dict)
        print(users.Users().users['admin']['username'])
        assert users.Users().users['admin']['username'] == 'admin'
