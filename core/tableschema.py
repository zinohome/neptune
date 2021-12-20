#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune


class TableSchema(object):
    def __init__(self, table_name, table_type):
        self._name = table_name
        self._type = table_type
        self._primarykeys = 'N/A'
        self._indexes = 'N/A'
        self._columns = 'N/A'
        self._dict = 'N/A'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def primarykeys(self):
        return self._primarykeys

    @primarykeys.setter
    def primarykeys(self, value):
        self._primarykeys = value

    @primarykeys.deleter
    def primarykeys(self):
        self._primarykeys = 'N/A'

    @property
    def indexes(self):
        return self._indexes

    @indexes.setter
    def indexes(self, value):
        self._indexes = value

    @indexes.deleter
    def indexes(self):
        self._indexes = 'N/A'

    @property
    def columns(self):
        return self._columns

    @columns.setter
    def columns(self, value):
        self._columns = value

    @columns.deleter
    def columns(self):
        self._columns = 'N/A'

    @property
    def dict(self):
        return self._dict

    @dict.setter
    def dict(self, value):
        self._dict = value

    @dict.deleter
    def dict(self):
        self._dict = 'N/A'

    def table2json(self):
        return {
            'name': self._name,
            'type': self._type,
            'primarykeys': self._primarykeys,
            'indexes': self._indexes,
            'columns': self._columns,
            'dict': self._dict
        }

    def getColumnType(self, Columename):
        rType = 'None'
        for column in self.columns:
            if column['name'] == Columename:
                rType = column['type']
                rType = rType[:rType.find("(")] if rType.find("(") > -1 else rType
                return rType
