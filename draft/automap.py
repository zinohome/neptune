#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sqlalchemy.ext.automap import automap_base
from core import dbengine, dbmeta


if __name__ == '__main__':
    engine = dbengine.DBEngine().connect()
    metadata = dbmeta.DBMeta().getmetadata()
    Base = automap_base(metadata=metadata)
    Base.prepare()
    for cls in Base.classes:
        print(cls)
    ncls = Base.classes['products']
    print(ncls)
    print(dir(ncls))
    print(ncls.__dict__)
