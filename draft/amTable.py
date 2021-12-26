#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from core import dbengine, dbmeta
from config import config
from util import log, toolkit
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker


'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)



if __name__ == '__main__':
    engine = dbengine.DBEngine().connect()
    meta = dbmeta.DBMeta()
    metadata = meta.metadata
    metadata.bind = engine
    Base = automap_base()
    Base.prepare(engine, reflect = True)
    log.logger.debug(dir(Base))
    log.logger.debug(dir(Base.classes))
    p = Base.classes['Models']
    log.logger.debug(p)
    for item in Base.classes:
        log.logger.debug(item)
    session_factory = sessionmaker(bind = engine)
    session = session_factory()
    scsession = scoped_session(session_factory)
    session = scsession(autoflush=True, autocommit=True)
    query = session.query(p).all()
    log.logger.debug(query)
