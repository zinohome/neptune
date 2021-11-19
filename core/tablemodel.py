#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

import sys
import traceback
import re
import decimal, datetime
from fastapi.encoders import jsonable_encoder
from core import dbengine, dbmeta
from config import config
from sqlalchemy import select
from sqlalchemy.sql import func
from util import log, toolkit
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker, scoped_session

'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])


class TableModel(object):
    def __init__(self, table_name):
        """Initialise the table from database schema."""
        meta = dbmeta.DBMeta()
        self._name = table_name
        self.engine = dbengine.DBEngine().connect()
        self._dbmeta = dbmeta.DBMeta()
        self._use_schema = cfg.database['db_use_schema']
        self.metadata = meta.metadata
        self.metadata.bind = self.engine
        self._schematable = self._dbmeta.gettable(table_name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def dbmeta(self):
        return self._dbmeta

    @dbmeta.setter
    def dbmeta(self, value):
        self._dbmeta = value

    @property
    def use_schema(self):
        return self._use_schema

    @use_schema.setter
    def use_schema(self, value):
        self._use_schema = value

    @property
    def schematable(self):
        return self._schematable

    @schematable.setter
    def schematable(self,value):
        self._schematable = value

    @property
    def exists(self):
        exist = False
        if self.metadata is not None:
            for tbl in self.metadata.sorted_tables:
                if self._name == tbl.name:
                    exist = True
                    break
        return exist

    @property
    def fullname(self):
        if self._dbmeta.use_schema:
            return self._dbmeta.schema + '.' + self._name
        else:
            return self._name

    @property
    def realtable(self):
        if self.exists:
            return self.metadata.tables[self.fullname]
        else:
            return None

    @property
    def columns(self):
        if isinstance(self.schematable.columns, str):
            return []
        else:
            return self.schematable.columns

    @property
    def columnvalues(self):
        cls = []
        if self.realtable is not None:
            cls = self.realtable.columns.values()
        return cls

    @property
    def primarykeys(self):
        if isinstance(self.schematable.primarykeys, str):
            return []
        else:
            return self.schematable.primarykeys

    @property
    def primarykeyvalues(self):
        cls = []
        if self.realtable is not None:
            cls = self.realtable.primary_key.columns.values()
        return cls

    def has_column(self, value):
        has = False
        for cl in self.columns:
            if cl['name'] == value:
                has = True
                break
        return has

    def alchemyencoder(obj):
        """JSON encoder function for SQLAlchemy special classes."""
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)

    def select(self, fieldlist='*', filter=None,
               filterparam=None,
               limit=cfg.query['query_default_limit'],
               offset=cfg.query['query_default_offset'],
               order=None, group=None, distinct=False,
               count_only=False, include_count=False):
        log.logger.debug('table select():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('fieldlist: %s' % fieldlist)
        log.logger.debug('filter: %s' % filter)
        log.logger.debug('limit: %s' % limit)
        log.logger.debug('offset: %s' % offset)
        log.logger.debug('order: %s' % order)
        log.logger.debug('group: %s' % group)
        log.logger.debug('distinct: %s' % distinct)
        log.logger.debug('count_only: %s' % count_only)
        log.logger.debug('include_count: %s' % include_count)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)

            cntsession_factory = sessionmaker(bind=self.engine)
            cntscsession = scoped_session(cntsession_factory)
            cntsession = cntscsession()

            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            select_cl = []
            if fieldlist == '*':
                select_st = select([rtable], distinct=distinct)
                count_st = select([func.count(next(iter(rtable.c))).label('col_count')], distinct=distinct)
            else:
                field_list = re.split(r'[\s\,\;]+', fieldlist)
                for cl in rtable.c:
                    if cl.name in field_list:
                        select_cl.append(cl)
                select_st = select(select_cl, distinct=distinct)
                count_st = select([func.count(select_cl[0]).label('col_count')], distinct=distinct)
            if limit > cfg.query['query_limit_upset']:
                limit = cfg.query['query_limit_upset']
            select_st = select_st.limit(limit).offset(offset)
            if order is not None:
                select_st = select_st.order_by(text(order))
            if group is not None:
                select_st = select_st.group_by(text(group))
            log.logger.debug('SQL of Select: [ %s ]' % select_st)
            log.logger.debug('SQL of Count: [ %s ]' % count_st)

            if filter is not None:
                select_st = select_st.where(text(filter))
                count_st = count_st.where(text(filter))
                filterparamdict = toolkit.to_dict(filterparam)
                if filterparamdict is not None:
                    cresult = cntsession.execute(count_st, filterparamdict)
                    result = session.execute(select_st, filterparamdict)
                else:
                    cresult = None
                    result = None
            else:
                cresult = cntsession.execute(count_st)
                result = session.execute(select_st)
            log.logger.debug('SQL of Query Full : [ %s ]' % select_st)
            log.logger.debug('SQL of Count Full : [ %s ]' % count_st)
            log.logger.debug('Select Count Result: [ %s ]' % cresult)
            crow = cresult.fetchone()
            colcount = crow['col_count']
            d, a = {}, []
            if result is not None:
                log.logger.debug('Select Result: [ %s ]' % result)
                log.logger.debug('Select Result Return : [ %s ] rows ' % result.rowcount)
                for row in result:
                    # result.items() returns an array like [(key0, value0), (key1, value1)]
                    for column, value in row._mapping.items():
                        # build up the dictionary
                        d = {**d, **{column: value}}
                    a.append(d)
                if bool(count_only):
                    return_json['record_count'] = colcount
                elif bool(include_count):
                    return_json['record_count'] = colcount
                    return_json['data'] = a
                else:
                    return_json['data'] = a
            else:
                return_json['data'] = None
        except Exception as e:
            log.logger.error('Exception at table select(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['selectResult'] = 'Error'
            return_json['selectError'] = 'Exception at table select(): %s ' % e
        finally:
            session.close()
            cntsession.close()
            scsession.remove()
            cntscsession.remove()
        return jsonable_encoder(return_json)

    def selectbyid(self, idvalue, fieldlist=None, idfiled=None):
        log.logger.debug('table selectbyid():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('idvalue: %s' % idvalue)
        log.logger.debug('fieldlist: %s' % fieldlist)
        log.logger.debug('idfiled: %s' % idfiled)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            select_cl = []
            if fieldlist is not None:
                if fieldlist == '*':
                    select_st = select([rtable])
                else:
                    field_list = toolkit.to_list(fieldlist)
                    for cl in rtable.c:
                        if cl.name in field_list:
                            select_cl.append(cl)
                    select_st = select(select_cl)
            else:
                select_st = select([rtable])
            log.logger.debug('SQL of Select: [ %s ]' % select_st)
            select_st = select_st.limit(cfg.query['query_limit_upset'])
            log.logger.debug('SQL of Select: [ %s ]' % select_st)
            l_pklist = []
            if idfiled is not None:
                l_pklist = toolkit.to_list(idfiled)
            else:
                l_pklist = self.primarykeys
            pkstr = None
            for pk in l_pklist:
                if pkstr is not None:
                    pkstr = pkstr + ' and ' + pk + '=:' + pk
                else:
                    pkstr = pk + '=:' + pk
            log.logger.debug('Primarykey select string : [ %s ]' % pkstr)
            pkparm = dict(zip(l_pklist, toolkit.to_list(idvalue)))
            typedpkparm = {}
            for (k, v) in pkparm.items():
                typedpkparm[k] = rtable.c[k].type.python_type(v)
            log.logger.debug('Primarykey select param : [ %s ]' % typedpkparm)
            if pkstr is not None:
                select_st = select_st.where(text(pkstr))
                if len(typedpkparm) >= len(l_pklist):
                    result = session.execute(select_st, typedpkparm)
                else:
                    result = None
            else:
                result = session.execute(select_st)
            log.logger.debug('SQL of Query: [ %s ]' % select_st)
            d, a = {}, []
            if result is not None:
                log.logger.debug('Select Result: [ %s ]' % result)
                log.logger.debug('Select Result Return : [ %s ] rows ' % result.rowcount)
                for row in result:
                    # result.items() returns an array like [(key0, value0), (key1, value1)]
                    for column, value in row._mapping.items():
                        # build up the dictionary
                        d = {**d, **{column: value}}
                    a.append(d)
                return_json['data'] = a
            else:
                return_json['data'] = None
        except Exception as e:
            log.logger.error('Exception at tablemodel selectbyid(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['selectResult'] = 'Error'
            return_json['selectError'] = 'Exception at tablemodel selectbyid(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)

    def insert(self, idfiled=None, fieldvalue=None):
        log.logger.debug('table insert():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('idfiled: %s' % idfiled)
        log.logger.debug('fieldvalue: %s' % fieldvalue)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            insert_st = rtable.insert()
            log.logger.debug('SQL of Insert: [ %s ]' % insert_st)
            fvl = toolkit.to_fvcol(fieldvalue)
            log.logger.debug('Insert Values: [ %s ]' % fvl)
            if fvl is not None:
                result = session.execute(insert_st, fvl)
                log.logger.debug('Insert Result: [ %s ]' % result)
                # log.logger.debug('Insert Result: [ %s ]' % json.dumps([dict(r) for r in result], default=self.alchemyencoder))
                # log.logger.debug('result.rowcount: [ %s ]' % result.rowcount)
                if result.rowcount > 0:
                    return_json['insert_row_id'] = result.inserted_primary_key[0]
                    return_json['insertResult'] = 'True'
                else:
                    return_json['insertResult'] = 'False'
            else:
                return_json['insert_row_id'] = -1
                return_json['insertResult'] = 'False'
        except Exception as e:
            log.logger.error('Exception at tablemodel insert(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['insertResult'] = 'Error'
            return_json['insertError'] = 'Exception at tablemodel insert(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)

    def update(self, filter=None, filterparam=None, fieldvalue=None):
        log.logger.debug('table udpate():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('filter: %s' % filter)
        log.logger.debug('filterparam: %s' % filterparam)
        log.logger.debug('fieldvalue: %s' % fieldvalue)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            update_st = rtable.update()
            log.logger.debug('SQL of Update: [ %s ]' % update_st)
            fvl = toolkit.to_fvcol(fieldvalue)
            log.logger.debug('Update Values: [ %s ]' % fvl)
            if filter is not None:
                update_st = update_st.where(text(filter))
                log.logger.debug('SQL of Update: [ %s ]' % update_st)
                if fvl is not None:
                    update_st = update_st.values(fvl)
                    log.logger.debug('SQL of Update: [ %s ]' % update_st)
                    filterparamdict = toolkit.to_dict(filterparam)
                    if filterparamdict is not None:
                        result = session.execute(update_st, filterparamdict)
                        log.logger.debug('Update Result: [ %s ]' % result)
                        return_json['udpate_rowcount'] = result.rowcount
                    else:
                        return_json['udpate_rowcount'] = 0
                else:
                    return_json['udpate_rowcount'] = 0
            else:
                return_json['udpate_rowcount'] = 0
        except Exception as e:
            log.logger.error('Exception at tablemodel update(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['updateResult'] = 'Error'
            return_json['updateError'] = 'Exception at tablemodel update(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)

    def updatebyid(self, idfiled=None, idvalue=None, fieldvalue=None):
        log.logger.debug('table udpatebyid():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('idfiled: %s' % idfiled)
        log.logger.debug('idvalue: %s' % idvalue)
        log.logger.debug('fieldvalue: %s' % fieldvalue)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            update_st = rtable.update()
            log.logger.debug('SQL of Update: [ %s ]' % update_st)
            lpklist = []
            if idfiled is not None:
                lpklist = toolkit.to_list(idfiled)
            else:
                lpklist = self.primarykeys
            ulpklist = toolkit.uappendlist(lpklist)
            pkstr = None
            for pk in lpklist:
                if pkstr is not None:
                    pkstr = pkstr + ' and ' + pk + '=:' + cfg.application['app_param_prefix'] + pk
                else:
                    pkstr = pk + '=:' + cfg.application['app_param_prefix'] + pk
            log.logger.debug('Primarykey select string : [ %s ]' % pkstr)
            pkparm = dict(zip(lpklist, toolkit.to_list(idvalue)))
            # pkparm = dict(zip(ulpklist, toolkit.to_list(idvalue)))
            typedpkparm = {}
            for (k, v) in pkparm.items():
                typedpkparm[k] = rtable.c[k].type.python_type(v)
            prlist = [v for v in typedpkparm.values()]
            submittypedpkparm = dict(zip(ulpklist, prlist))
            log.logger.debug('Primarykey select param : [ %s ]' % submittypedpkparm)
            fvl = toolkit.to_fvcol(fieldvalue)
            if pkstr is not None:
                update_st = update_st.where(text(pkstr))
                if fvl is not None:
                    update_st = update_st.values(fvl)
                    log.logger.debug('SQL of Update: [ %s ]' % update_st)
                    if len(submittypedpkparm) >= len(lpklist):
                        result = session.execute(update_st, submittypedpkparm)
                        log.logger.debug('Update Result: [ %s ]' % result)
                        return_json['udpate_rowcount'] = result.rowcount
                    else:
                        return_json['udpate_rowcount'] = 0
                else:
                    return_json['udpate_rowcount'] = 0
            else:
                return_json['udpate_rowcount'] = 0
        except Exception as e:
            log.logger.error('Exception at tablemodel updatebyid(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['updateResult'] = 'Error'
            return_json['updateError'] = 'Exception at tablemodel updatebyid(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)

    def delete(self, filter=None, filterparam=None):
        log.logger.debug('table delete():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('filter: %s' % filter)
        log.logger.debug('filterparam: %s' % filterparam)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            delete_st = rtable.delete()
            log.logger.debug('SQL of Delete: [ %s ]' % delete_st)
            if filter is not None:
                delete_st = delete_st.where(text(filter))
                filterparamdict = toolkit.to_dict(filterparam)
                if filterparamdict is not None:
                    result = session.execute(delete_st, filterparamdict)
                    log.logger.debug('Delete Result: [ %s ]' % result)
                    return_json['delet_rowcount'] = result.rowcount
                else:
                    return_json['delet_rowcount'] = 0
            else:
                return_json['delet_rowcount'] = 0
        except Exception as e:
            log.logger.error('Exception at tablemodel delete(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['deleteResult'] = 'Error'
            return_json['deleteError'] = 'Exception at tablemodel delete(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)

    def deletebyid(self, idfiled=None, idvalue=None):
        log.logger.debug('table delete():')
        log.logger.debug('tablename: %s' % self._name)
        log.logger.debug('idfiled: %s' % idfiled)
        log.logger.debug('idvalue: %s' % idvalue)
        return_json = {}
        try:
            session_factory = sessionmaker(bind=self.engine)
            scsession = scoped_session(session_factory)
            session = scsession(autoflush=True, autocommit=True)
            rtable = self.realtable
            log.logger.debug('TableModel Columns: %s' % self.columnvalues)
            delete_st = rtable.delete()
            log.logger.debug('SQL of Delete: [ %s ]' % delete_st)
            lpklist = []
            if idfiled is not None:
                lpklist = toolkit.to_list(idfiled)
            else:
                lpklist = self.primarykeys
            pkstr = None
            for pk in lpklist:
                if pkstr is not None:
                    pkstr = pkstr + ' and ' + pk + '=:' + pk
                else:
                    pkstr = pk + '=:' + pk
            log.logger.debug('Primarykey select string : [ %s ]' % pkstr)
            pkparm = dict(zip(lpklist, toolkit.to_list(idvalue)))
            typedpkparm = {}
            for (k, v) in pkparm.items():
                typedpkparm[k] = rtable.c[k].type.python_type(v)
            log.logger.debug('Primarykey select param : [ %s ]' % typedpkparm)
            if pkstr is not None:
                delete_st = delete_st.where(text(pkstr))
                log.logger.debug('SQL of Delete: [ %s ]' % delete_st)
                if len(typedpkparm) >= len(lpklist):
                    result = session.execute(delete_st, typedpkparm)
                    log.logger.debug('Delete Result: [ %s ]' % result)
                    return_json['delet_rowcount'] = result.rowcount
                else:
                    return_json['delet_rowcount'] = 0
            else:
                return_json['delet_rowcount'] = 0
        except Exception as e:
            log.logger.error('Exception at tablemodel deletebyid(): %s ' % e)
            if cfg.application['app_exception_detail']:
                traceback.print_exc(limit=3, file=sys.stdout)
            return_json['deleteResult'] = 'Error'
            return_json['deleteError'] = 'Exception at tablemodel deletebyid(): %s ' % e
        finally:
            session.close()
            scsession.remove()
        return jsonable_encoder(return_json)


if __name__ == '__main__':

    '''
    table = TableModel('orders')
    log.logger.debug(table.exists)
    log.logger.debug(table.fullname)
    log.logger.debug(table.realtable)
    log.logger.debug(table.schematable.columns)
    log.logger.debug(table.columns)
    log.logger.debug(table.columnvalues)
    log.logger.debug(table.has_column('requiredDate'))
    log.logger.debug(table.has_column('Date'))
    log.logger.debug(table.primarykeys)
    log.logger.debug(table.primarykeyvalues)
    result = table.insert('id','{\'name\':\'sdf\',\'phone\':\'234243\'}')
    log.logger.debug(result)
    did = result['insert_row_id']
    #dresult = table.delete('(id=:pid)','{\'pid\':'+str(did)+'}')
    #dresult = table.deletebyid('id', str(did))
    #dresult = table.update('id=:pid', {'pid':did}, '{\'name\':\'jjjjhhhh\',\'phone\':\'0009999\'}')
    dresult = table.updatebyid(None, did, '{\'name\':\'jjjjhhhh\',\'phone\':\'0009999\'}')
    log.logger.debug(dresult)
    #sresult = table.select('*','id=:pid', {'pid':did},20,0,None,None,True,False,False)
    sresult = table.select('name',None, None,20,0,None,None,True,False,False)
    log.logger.debug(sresult)
    ssresult = table.selectbyid(1101867,'name,id', 'id')
    log.logger.debug(ssresult)

    '''
    table = TableModel('orders')
    sresult = table.select('*', None, None, 20, 20, None, None, False, False, False)
    #sresult = table.selectbyid('10114', 'customerNumber,orderDate')
    log.logger.debug(sresult)


