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
from sqlalchemy import inspect, Table
from sqlalchemy.schema import MetaData,CreateTable
import simplejson as json
from config import config
from util import log, toolkit
import pickle
import base64
import uuid

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
        self.gen_dbdirgramcanvas()
        self.gen_ddl()

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
            if tb.type == 'table':
                tblist.append(tb.name)
        return tblist

    def get_views(self):
        viewlist = []
        for tb in self._tables:
            if tb.type == 'view':
                viewlist.append(tb.name)
        return viewlist

    def response_schema(self):
        tblist = []
        for tb in self._tables:
            tblist.append(tb.name)
        return tblist

    def gen_dbdirgram(self):
        try:
            basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
            apppath = os.path.abspath(os.path.join(basepath, os.pardir))
            configpath = os.path.abspath(os.path.join(apppath, 'config'))
            canvasfilepath = os.path.abspath(os.path.join(configpath, "dbdiagram-canvas.json"))
            diagramfilepath = os.path.abspath(os.path.join(configpath, "dbdiagram.json"))
            dbdiagram={}
            canvas = {}
            with open(canvasfilepath, 'r') as canvasfile:
                canvas = json.loads(canvasfile.read())
            canvas['databaseName'] = cfg['Database_Config'].db_name
            dbdiagram['canvas'] = canvas
            tables = self.get_tables()
            tbllist = []
            for tbl in tables:
                dgtable = self.gettable(tbl)
                ndgtable = {}
                ndgtable['name'] = dgtable.name
                ndgtable['comment'] = ''
                ndgtable['id'] = str(uuid.uuid1())
                ndgtable['ui'] = {'active':True,'left':50,'top':50,'zIndex':1,'widthName':60,'widthComment':60}
                ndgcolume = {}
                pks = dgtable.primarykeys
                clmlist = []
                for clm in dgtable.columns:
                    ndgcolume = {}
                    ndgcolume['id'] = str(uuid.uuid1())
                    ndgcolume['name'] = clm['name']
                    ndgcolume['comment'] = '' if clm['comment'] == 'None' else clm['comment']
                    ndgcolume['dataType'] = clm['type']
                    ndgcolume['default'] =  '' if clm['default'] == 'None' else clm['default']
                    ndgcolume['option'] = {"autoIncrement": False,"primaryKey": False,"unique": False,"notNull": False}
                    ndgcolume['ui'] = {"active": False, "pk": False, "fk": False, "pfk": False, "widthName": 60,
                                       "widthComment": 60, "widthDataType": 60, "widthDefault": 60}
                    if clm.__contains__('nullable'):
                        ndgcolume['option']['notNull'] = 'true' if clm['nullable'] == 'False' else 'false'
                    if clm.__contains__('autoincrement'):
                        ndgcolume['option']['autoIncrement'] = clm['autoincrement']
                    if clm['name'] in pks:
                        ndgcolume['option']['primaryKey'] = True
                        ndgcolume['ui']['pk'] = True
                    clmlist.append(ndgcolume)
                ndgtable['columns'] = clmlist
                tbllist.append(ndgtable)
            dbdiagramtable = {}
            dbdiagramtable['tables'] = tbllist
            dbdiagram['table'] = dbdiagramtable
            #log.logger.debug(dbdiagram)
            with open(diagramfilepath, 'w', encoding='utf-8') as diagramfile:
                json.dump(dbdiagram, diagramfile, separators=(',', ':'),
                          sort_keys=False, indent=4, ensure_ascii=False, encoding='utf-8')
        except Exception as exp:
            log.logger.error('Exception at gen_dbdirgram() %s ' % exp)


    def gen_dbdirgramcanvas(self):
        try:
            basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
            apppath = os.path.abspath(os.path.join(basepath, os.pardir))
            configpath = os.path.abspath(os.path.join(apppath, 'config'))
            canvasfilepath = os.path.abspath(os.path.join(configpath, "dbdiagram-canvas.json"))
            diagramfilepath = os.path.abspath(os.path.join(configpath, "dbdiagram.json"))
            dbdiagram={}
            canvas = {}
            with open(canvasfilepath, 'r') as canvasfile:
                canvas = json.loads(canvasfile.read())
            canvas['databaseName'] = cfg['Database_Config'].db_name
            dbdiagram['canvas'] = canvas
            #log.logger.debug(dbdiagram)
            with open(diagramfilepath, 'w', encoding='utf-8') as diagramfile:
                json.dump(dbdiagram, diagramfile, separators=(',', ':'),
                          sort_keys=False, indent=4, ensure_ascii=False, encoding='utf-8')
        except Exception as exp:
            log.logger.error('Exception at gen_dbdirgram() %s ' % exp)


    def gen_ddl(self):
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        configpath = os.path.abspath(os.path.join(apppath, 'config'))
        ddlfilepath = os.path.abspath(os.path.join(configpath, "dbddl.sql"))
        engine = dbengine.DBEngine().connect()
        inspector = inspect(engine)
        metadata = self.metadata
        ddlstr = ''
        try:
            if metadata is not None:
                log.logger.debug("Generate Schema from : [ %s ] with db schema "
                                 "[ %s ]" % (cfg['Database_Config'].db_name, self._schema))
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
                        tblcrtstr = str(CreateTable(user_table).compile(engine))
                        tblcrtstr = tblcrtstr.replace(' ' + self._schema + '.', ' ')
                        tblcrtstr = tblcrtstr.replace(' '+table_name+' ',' `'+table_name+'` ')
                        table_columns = inspector.get_columns(table_name)
                        if self.use_schema:
                            table_columns = inspector.get_columns(table_name, schema=self._schema)
                        for column in table_columns:
                            tblcrtstr = tblcrtstr.replace('\t'+column['name'] + ' ', '\t`' + column['name'] + '` ')
                            tblcrtstr = tblcrtstr.replace('(' + column['name'] + ')', ' `(' + column['name'] + '`) ')
                        #log.logger.debug(tblcrtstr)
                        ddlstr = ddlstr + tblcrtstr
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
                        viewcrtstr = str(CreateTable(user_view).compile(engine))
                        viewcrtstr = viewcrtstr.replace(' ' + self._schema + '.', ' ')
                        viewcrtstr = viewcrtstr.replace(' ' + view_name + ' ', ' `' + view_name + '` ')
                        view_columns = inspector.get_columns(view_name)
                        if self.use_schema:
                            view_columns = inspector.get_columns(view_name, schema=self._schema)
                        for vcolumn in view_columns:
                            viewcrtstr = viewcrtstr.replace('\t' + vcolumn['name'] + ' ', '\t`' + vcolumn['name'] + '` ')
                            viewcrtstr = viewcrtstr.replace('(' + vcolumn['name'] + ')', ' `(' + vcolumn['name'] + '`) ')
                        #log.logger.debug(viewcrtstr)
                        ddlstr = ddlstr + viewcrtstr
                #log.logger.debug(ddlstr)
                with open(ddlfilepath, 'w', encoding='utf-8') as ddlfile:
                    ddlfile.write(ddlstr)
                    ddlfile.close()
            else:
                log.logger.error('Can not get metadata at gen_ddl() ... ')
                raise Exception('Can not get metadata at gen_ddl()')
        except Exception as exp:
            log.logger.error('Exception at gen_ddl() %s ' % exp)


    def response_dbdiagram(self, filename, canvasonly=False):
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        configpath = os.path.abspath(os.path.join(apppath, 'config'))
        diagramfilepath = os.path.abspath(os.path.join(configpath, filename))
        rjson = {"name":filename,
                 "type": "file",
                 "content": ""}
        with open(diagramfilepath, 'r') as diagramfile:
            rjson['content'] = base64.b64encode(diagramfile.read().encode('utf-8'))
        return rjson

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
    log.logger.debug(cfg['Database_Config'].db_schema)
    meta = DBMeta()
    metadata = meta.metadata
    otable = meta.gettable('customers')
    log.logger.debug(meta.get_tables())
    log.logger.debug(meta.get_views())
    #meta.gen_dbdirgram()
    meta.gen_dbdirgramcanvas()
    meta.gen_ddl()

    '''
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
    log.logger.debug(meta.response_dbdiagram())
    '''
