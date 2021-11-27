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
from core import dbengine, tableschema
from sqlalchemy import inspect, MetaData, Table
import simplejson as json
from config import config
from util import log, toolkit
import pickle

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

# cache file define
metadata_pickle_filename = cfg['Schema_Config'].schema_cache_filename
cache_path = os.path.join(os.path.expanduser("~"), ".neptune_cache")


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class DBMeta(object):
    def __init__(self):
        self.use_schema = cfg['Database_Config'].db_use_schema
        self._schema = cfg['Database_Config'].db_schema
        self._tableCount = 0
        self._tables = 'N/A'
        self._viewCount = 0
        self._metadata = None
        self.load_metadata()
        if cfg['Application_Config'].app_force_generate_meta:
            log.logger.debug('Generate Schema file from database ...')
            self.gen_schema()
        else:
            if os.path.exists(self.schema_file):
                log.logger.debug('Schema file exists, you can load it to application ...')
            else:
                log.logger.debug('Schema file does not exists, generate it from database ...')
                self.gen_schema()
        self.load_schema()

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self, value):
        self._schema = value

    @property
    def tablecount(self):
        return self._tableCount

    @property
    def tables(self):
        return self._tables

    @property
    def viewcount(self):
        return self._viewCount

    @property
    def metadata(self):
        if self._metadata is not None:
            return self._metadata
        else:
            return None

    @property
    def schema_file(self):
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        configpath = os.path.abspath(os.path.join(apppath, 'config'))
        metafilepath = os.path.abspath(os.path.join(configpath, cfg['Schema_Config'].schema_db_metafile))
        return metafilepath

    def load_metadata(self):
        engine = dbengine.DBEngine().connect()
        cached_metadata = None
        if cfg['Schema_Config'].schema_cache_enabled:
            if os.path.exists(os.path.join(cache_path, metadata_pickle_filename)):
                try:
                    with open(os.path.join(cache_path, metadata_pickle_filename), 'rb') as cache_file:
                        cached_metadata = pickle.load(file=cache_file)
                        log.logger.debug('Metadata cache exists, load meta from cache '
                                         'file [ %s ]' % os.path.join(cache_path, metadata_pickle_filename))
                except IOError:
                    # cache file not found - no problem, reflect as usual
                    log.logger.debug('Metadata cache does not exists, will generate it from database ...')
            if cached_metadata:
                cached_metadata.bind = engine
                self._metadata = cached_metadata
            else:
                metadata = MetaData(bind=engine)
                if self.use_schema:
                    metadata = MetaData(bind=engine, schema=self._schema)
                if cfg['Schema_Config'].schema_fetch_all_table == True:
                    metadata.reflect(views=True)
                else:
                    metadata.reflect(views=True, only=toolkit.to_list(cfg['Schema_Config'].schema_fetch_tables))
                self._metadata = metadata
                try:
                    if not os.path.exists(cache_path):
                        os.makedirs(cache_path)
                    with open(os.path.join(cache_path, metadata_pickle_filename), 'wb') as cache_file:
                        pickle.dump(metadata, cache_file)
                        log.logger.debug('Metadata cache save to '
                                         '[ %s ] ' % os.path.join(cache_path, metadata_pickle_filename))
                except:
                    # couldn't write the file for some reason
                    log.logger.debug('Metadata save Error '
                                     '[ %s ] ' % os.path.join(cache_path, metadata_pickle_filename))
        else:
            metadata = MetaData(bind=engine)
            if self.use_schema:
                metadata = MetaData(bind=engine, schema=self._schema)
            if cfg['Schema_Config'].schema_fetch_all_table == True:
                metadata.reflect(views=True)
            else:
                metadata.reflect(views=True, only=toolkit.to_list(cfg['Schema_Config'].schema_fetch_tables))
            self._metadata = metadata

    def gen_schema(self):
        engine = dbengine.DBEngine().connect()
        inspector = inspect(engine)
        metadata = self.metadata
        try:
            if metadata is not None:
                log.logger.debug("Generate Schema from : [ %s ] with db schema "
                                 "[ %s ]" % (cfg['Database_Config'].db_name, self._schema))
                jmeta = {}
                jmeta['Schema'] = cfg['Database_Config'].db_schema
                jtbls = {}
                jmeta['Tables'] = jtbls
                table_list_set = set(toolkit.to_list(cfg['Schema_Config'].schema_fetch_tables))
                table_names = inspector.get_table_names()
                if self.use_schema:
                    table_names = inspector.get_table_names(schema=self._schema)
                for table_name in table_names:
                    persist_table = False
                    if cfg['Schema_Config'].schema_fetch_all_table:
                        persist_table = True
                    else:
                        if table_name in table_list_set:
                            persist_table = True
                    if persist_table:
                        user_table = Table(table_name, metadata, autoload_with=engine)
                        jtbl = {}
                        jtbls[table_name] = jtbl
                        jtbl['Name'] = table_name
                        jtbl['Type'] = 'table'
                        pk = inspector.get_pk_constraint(table_name)
                        if self.use_schema:
                            pk = inspector.get_pk_constraint(table_name, schema=self._schema)
                        if len(pk) > 0:
                            jtbl['PrimaryKeys'] = pk['constrained_columns']
                        else:
                            jtbl['PrimaryKeys'] = []
                        jtbl['Indexes'] = inspector.get_indexes(table_name)
                        if self.use_schema:
                            jtbl['Indexes'] = inspector.get_indexes(table_name, schema=self._schema)
                        jtbl['Columns'] = []
                        table_columns = inspector.get_columns(table_name)
                        if self.use_schema:
                            table_columns = inspector.get_columns(table_name, schema=self._schema)
                        for column in table_columns:
                            cdict={}
                            for key, value in column.items():
                                cdict[key] = value.__str__()
                            jtbl['Columns'].append(cdict)
                        jtbl['Dict'] = json.loads(json.dumps(user_table.__dict__,
                                                             indent=4, sort_keys=True, default=str))
                view_names = inspector.get_view_names()
                if self.use_schema:
                    view_names = inspector.get_view_names(schema=self._schema)
                for view_name in view_names:
                    persist_view = False
                    if cfg['Schema_Config'].schema_fetch_all_table:
                        persist_view = True
                    else:
                        if view_name in table_list_set:
                            persist_view = True
                    if persist_view:
                        user_view = Table(view_name, metadata, autoload_with=engine)
                        vtbl = {}
                        jtbls[view_name] = vtbl
                        vtbl['Name'] = view_name
                        vtbl['Type'] = 'view'
                        pk = inspector.get_pk_constraint(view_name)
                        if self.use_schema:
                            pk = inspector.get_pk_constraint(view_name, schema=self._schema)
                        if len(pk) > 0:
                            vtbl['PrimaryKeys'] = pk['constrained_columns']
                        else:
                            vtbl['PrimaryKeys'] = []
                        vtbl['Indexes'] = inspector.get_indexes(view_name)
                        if self.use_schema:
                            vtbl['Indexes'] = inspector.get_indexes(view_name, schema=self._schema)
                        vtbl['Columns'] = []
                        view_columns = inspector.get_columns(view_name)
                        if self.use_schema:
                            view_columns = inspector.get_columns(view_name, schema=self._schema)
                        for vcolumn in view_columns:
                            vdict = {}
                            for key, value in vcolumn.items():
                                vdict[key] = value.__str__()
                            vtbl['Columns'].append(vdict)
                        vtbl['Dict'] = json.loads(
                            json.dumps(user_view.__dict__, indent=4, sort_keys=True, default=str))
                with open(self.schema_file, 'w') as jsonfile:
                    json.dump(jmeta, jsonfile, separators=(',', ':'),
                              sort_keys=False, indent=4, ensure_ascii=False, encoding='utf-8')
            else:
                log.logger.error('Can not get metadata at gen_schema() ... ')
                raise Exception('Can not get metadata at gen_schema()')
        except Exception as exp:
            log.logger.error('Exception at gen_schema() %s ' % exp)

    def load_schema(self):
        log.logger.debug('Loading schema from %s' % self.schema_file)
        with open(self.schema_file, 'r') as schemafile:
            jschema = json.loads(schemafile.read())
            self._schema = jschema['Schema']
            if len(jschema['Tables']) > 0:
                self._tables = []
                for jtbname in jschema['Tables']:
                    jtable = jschema['Tables'][jtbname]
                    table = tableschema.TableSchema(jtable['Name'], jtable['Type'])
                    for elename in jtable:
                        if elename == 'PrimaryKeys':
                            table.primarykeys = jtable[elename]
                        elif elename == 'Indexes':
                            table.indexes = jtable[elename]
                        elif elename == 'Columns':
                            table.columns = jtable[elename]
                        elif elename == 'Dict':
                            table.dict = jtable[elename]
                    self._tables.append(table)
                    if table.type == 'table':
                        self._tableCount = self._tableCount + 1
                    if table.type == 'view':
                        self._viewCount = self._viewCount + 1
        log.logger.debug('Schema load with [ %s ] tables and [ %s ] views' % (self._tableCount, self._viewCount))

    def gettable(self, value):
        if len(self._tables) > 0:
            for table in self._tables:
                if table.name == value:
                    return table
        else:
            return None

    def get_table_primary_keys(self, value):
        table = self.gettable(value)
        if table is not None:
            pks = table.primarykeys
            if pks == 'N/A':
                pks = []
            return pks
        else:
            return None

    def get_tables(self):
        tblist = []
        for tb in self._tables:
            if table.type == 'table':
                tblist.append(tb.name)
        return tblist

    def get_views(self):
        viewlist = []
        for tb in self._tables:
            if table.type == 'view':
                viewlist.append(tb.name)
        return viewlist

    def response_schema(self):
        tblist = []
        for tb in self._tables:
            tblist.append(tb.name)
        return tblist

    def response_table_schema(self, value):
        tb = self.gettable(value)
        if tb is not None:
            return tb.table2json()
        else:
            return {}

    def check_table_schema(self, value):
        tb = self.gettable(value)
        if tb is not None:
            return True
        else:
            return False


if __name__ == '__main__':
    meta = DBMeta()
    metadata = meta.metadata
    otable = meta.gettable('customers')
    log.logger.debug(otable.table2json())
    log.logger.debug("****************************************************")
    if metadata is not None:
        for item in dir(metadata):
            log.logger.debug(item)
        log.logger.debug("===================================================")
        for table in metadata.sorted_tables:
            log.logger.debug(table.name)
    log.logger.debug("****************************************************")
    log.logger.debug(meta.schema_file)
