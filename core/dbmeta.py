#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from core import dbengine, tableschema
from sqlalchemy import inspect, MetaData
import simplejson as json
from config import config
from util import log
import pickle

'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])

# cache file define
metadata_pickle_filename = cfg.schema['schema_cache_filename']
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
        self.use_schema = cfg.database['db_use_schema']
        self._schema = cfg.database['db_schema']
        self._tableCount = 0
        self._tables = 'N/A'
        self._viewCount = 0
        self._metadata = None
        self.load_metadata()
        if cfg.application['app_force_generate_meta']:
            log.logger.debug('Generate Schema file from database ...')
            self.gen_schema()
        else:
            if os.path.exists(self.get_schema_file()):
                log.logger.debug('Schema file exists, you can load it to application ...')
            else:
                log.logger.debug('Schema file does not exists, generate it from database ...')
                self.gen_schema()
        self.load_schema()

    @property
    def schema(self):
        return self._schema

    @schema.setter
    def schema(self,value):
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

    def load_metadata(self):
        engine = dbengine.DBEngine().connect()
        cached_metadata = None
        if cfg.schema['schema_cache_enabled']:
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
                if cfg.schema['schema_fetch_all_table']:
                    metadata.reflect(views=True)
                else:
                    metadata.reflect(views=True, only=cfg.schema['schema_fetch_tables'])
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
                self._metadata = metadata
        else:
            metadata = MetaData(bind=engine)
            if self.use_schema:
                metadata = MetaData(bind=engine, schema=self._schema)
            if cfg.schema['schema_fetch_all_table']:
                metadata.reflect(views=True)
            else:
                metadata.reflect(views=True, only=cfg.schema['schema_fetch_tables'])
            self._metadata = metadata

    def gen_schema(self):
        engine = dbengine.DBEngine().connect()
        inspector = inspect(engine)
        metadata = self.metadata()
        try:
            if metadata is not None:
                log.logger.debug("Generate Schema from : [ %s ] with db schema "
                                 "[ %s ]" % (cfg.database['db_name'], self._schema))
                jmeta = {}
                jmeta['Schema'] = cfg.database['db_schema']
                jtbls = {}
                jmeta['Tables'] = jtbls
                table_list_set = set(cfg.schema['schema_fetch_tables'])
                table_names = inspector.get_table_names()
                if self.use_schema:
                    table_names = inspector.get_table_names(schema=self._schema)
                for table_name in table_names:
                    persist_table = False
                    if cfg.schema['schema_fetch_all_table']:
                        persist_table = True
                    else:
                        if table_name in table_list_set:
                            persist_table = True
                    if persist_table:
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
                        table_columes = inspector.get_columns(table_name)
                        if self.use_schema:
                            table_columes = inspector.get_columns(table_name, schema=self._schema)
                        for column in table_columes:
                            if len(column) > 0:
                                jtbl['Columns'].append(json.loads(json.dumps(column.__str__(), separators=(',', ':'))))

                view_names = inspector.get_view_names()
                if self.use_schema:
                    view_names = inspector.get_view_names(schema=self._schema)
                for view_name in view_names:
                    persist_table = False
                    if cfg.schema['schema_fetch_all_table']:
                        persist_table = True
                    else:
                        if view_name in table_list_set:
                            persist_table = True
                    if persist_table:
                        for table_v in reversed(metadata.sorted_tables):
                            if table_v.name == view_name:
                                vtbl = {}
                                jtbls[view_name] = vtbl
                                vtbl['Name'] = view_name
                                vtbl['Type'] = 'view'
                                vtbl['Columns'] = []
                                for v_column in table_v.columns:
                                    if len(v_column) > 0:
                                        vtbl['Columns'].append(json.loads(json.dumps(v_column.__str__(), separators=(',', ':'))))
                with open(self.get_schema_file(), 'w') as jsonfile:
                    json.dump(jmeta, jsonfile, separators=(',', ':'), sort_keys=False, indent=4 * ' ', ensure_ascii=False, encoding='utf-8')

            else:
                log.logger.error('Can not get metadata at genschema() ... ')
                raise Exception('Can not get metadata at genschema()')
        except Exception as err:
            log.logger.error('Exception get metadata at genschema() %s ' % err)

    def load_schema(self):
        log.logger.debug('Loading schema from %s' % self.get_schema_file())
        with open(self.get_schema_file(), 'r') as metafile:
            jmeta = json.loads(metafile.read())
            self._schema = jmeta['Schema']
            if len(jmeta['Tables']) > 0:
                self._tables = []
                for jtbname in jmeta['Tables']:
                    jtable = jmeta['Tables'][jtbname]
                    table = tableschema.TableSchema(jtable['Name'], jtable['Type'])
                    for elename in jtable:
                        log.logger.critical(elename)
                        if elename == 'PrimaryKeys':
                            table.primarykeys = jtable[elename]
                        elif elename == 'Indexes':
                            table.indexes = jtable[elename]
                        elif elename == 'Columns':
                            table.columns = jtable[elename]
                    self._tables.append(table)
                    if table.type == 'table':
                        self._tableCount = self._tableCount + 1
                    if table.type == 'view':
                        self._viewCount = self._viewCount + 1
        log.logger.debug('Schema load with [ %s ] tables and [ %s ] views' % (self._tableCount, self._viewCount))

    def get_schema_file(self):
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        configpath = os.path.abspath(os.path.join(apppath, 'config'))
        metafilepath = os.path.abspath(os.path.join(configpath, cfg.schema['schema_db_metafile']))
        return metafilepath

    def gettable(self, tablename):
        if len(self._tables) > 0:
            for table in self._tables:
                if table.getname() == tablename:
                    return table
        else:
            return None

    def gettablekey(self, tablename):
        table = self.gettable(tablename)
        if table is not None:
            pks = table.getprimarykeys()
            if pks == 'N/A':
                pks = []
            return pks
        else:
            return None

    def response_schema(self):
        tblist = []
        for tb in self._tables:
            tblist.append(tb.name)
        return tblist

    def response_table_schema(self, tablename):
        tb = self.gettable(tablename)
        if tb is not None:
            return tb.table2json()
        else:
            return {}

    def check_table_schema(self, tablename):
        tb = self.gettable(tablename)
        if tb is not None:
            return True
        else:
            return False


if __name__ == '__main__':
    dbmeta = DBMeta()
    metadata = dbmeta.metadata()
    log.logger.debug("****************************************************")
    if metadata is not None:
        for item in dir(metadata):
            log.logger.debug(item)
        log.logger.debug("===================================================")
        for table in metadata.sorted_tables:
            log.logger.debug(table.name)
    log.logger.debug("****************************************************")
    log.logger.debug(dbmeta.get_schema_file())
