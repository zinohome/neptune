#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from sqlalchemy.ext.automap import automap_base
from core import dbengine, dbmeta
from sqlalchemy import inspect, MetaData, Table

from util import log
def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

if __name__ == '__main__':
    engine = dbengine.DBEngine().connect()
    metadata = dbmeta.DBMeta().metadata
    Base = automap_base(metadata=metadata)
    Base.prepare()
    #for cls in Base.classes:
    #    print(cls)
    #ncls = Base.classes['products']
    #print(ncls)
    #print(dir(ncls))
    #print(ncls.__dict__)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    for table_name in table_names:
        user_table = Table(table_name, metadata, autoload_with=engine)
        #inspector.reflect_table(user_table, None)
        log.logger.debug(user_table.__dict__)
        log.logger.debug(json.dumps(user_table.__dict__, indent=4, sort_keys=True, default=str))
        log.logger.error(user_table.name)
        log.logger.error(user_table.indexes)
        log.logger.error(user_table.primary_key)
        log.logger.error(user_table._columns)
    view_names = inspector.get_view_names()
    for view_name in view_names:
        user_view = Table(view_name, metadata, autoload_with=engine)
        #inspector.reflect_table(user_view, None)
        log.logger.success(user_view.__dict__)
        log.logger.debug(json.dumps(user_view.__dict__, indent=4, sort_keys=True, default=str))
        log.logger.critical(user_view.name)
        log.logger.critical(user_view.indexes)
        log.logger.critical(user_view.primary_key)
        log.logger.critical(user_view._columns)


