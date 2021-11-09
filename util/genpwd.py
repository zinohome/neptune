#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


if __name__ == '__main__':
    '''
    plain_password = 'passw0rd'
    hashed_password = get_password_hash(plain_password)
    print('The hashed password of [ %s ] is [ %s ]' % (plain_password, hashed_password))
    print('Verify again: [ %s ]' % verify_password(plain_password, hashed_password))
    '''
