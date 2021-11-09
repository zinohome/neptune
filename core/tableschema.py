#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class TableSchema(object):
    def __init__(self, name, type):
        self.__name = name
        self.__type = type
        self.__primarykeys = 'N/A'
        self.__indexes = 'N/A'
        self.__columns = 'N/A'

    def getname(self):
        return self.__name

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
