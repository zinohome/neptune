#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy import Table

class TableSchema(object):
    def __init__(self, name, type):
        self._name = name
        self._type = type
        self._primarykeys = 'N/A'
        self._indexes = 'N/A'
        self._columns = 'N/A'

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def gettype(self):
        return self.__type

    def getprimarykeys(self):
        return self.__primarykeys

    def getindexes(self):
        return self.__indexes

    def getcolumns(self):
        return self.__columns

    def setprimarykeys(self, primarykeys):
        self.__primarykeys = primarykeys

    def setindexes(self, indexes):
        self.__indexes = indexes

    def setcolumns(self, columns):
        self.__columns = columns


    def table2json(self):
        return {
            'name': self.__name,
            'type': self.__type,
            'primarykeys': self.__primarykeys,
            'indexes': self.__indexes,
            'columns': self.__columns
        }
