#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune


from pydantic import BaseModel
from config import config


class TableQueryBody(BaseModel):
    fieldlist: str = '*'
    filter: str = None
    filterparam: str = None
    limit: int = config.app_config['Query_Config'].query_default_limit
    offset: int = config.app_config['Query_Config'].query_default_offset
    order: str = None
    group: str = None
    distinct: bool = False
    count_only: bool = False
    include_count: bool = False


class TableQueryByIdBody(BaseModel):
    fieldlist: str = '*'
    idfield: str = None
    id: str = None


class TablePostBody(BaseModel):
    fieldvalue: str = None
    idfield: str = None


class TablePutByIdBody(BaseModel):
    fieldvalue: str = None
    idfield: str = None


class TablePutBody(BaseModel):
    filter: str = None
    filterparam: str = None
    fieldvalue: str = None


class UserFuncPostBody(BaseModel):
    sqlparam: str = None
