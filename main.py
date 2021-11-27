#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune
from starlette.responses import FileResponse

from util import toolkit, log
from config import config, querydef
from fastapi import FastAPI, Header, Depends, HTTPException
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware
from flask import Flask
from importlib import import_module
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
import os
from fastapi.security import OAuth2PasswordRequestForm
from auth import users
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from starlette.responses import RedirectResponse
from core import security, dbengine, tablemodel, apimodel, userfunc
from datetime import timedelta
from core import dbmeta as meta
from admin.apps import login_manager


'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

'''app_dir'''
app_dir = os.path.dirname(os.path.abspath(__file__))

'''API prefix'''
prefix = cfg['Application_Config'].app_prefix
if prefix.startswith('/'):
    pass
else:
    prefix = '/' + prefix
log.logger.info(cfg['Application_Config'].app_name + ' Start Up ....')
log.logger.info("API prefix is: [ %s ]" % prefix)

'''API define'''
app = FastAPI(
    title=cfg['Application_Config'].app_name,
    description=cfg['Application_Config'].app_description,
    version=cfg['Application_Config'].app_version,
    openapi_url=prefix+"/openapi.json",
    docs_url=None,
    redoc_url=None
)

favicon_path = 'static/favicon.ico'
app.mount("/static", StaticFiles(directory="admin/apps/static"), name="static")


@app.on_event("startup")
async def startup_event():
    log.logger.info(cfg['Application_Config'].app_name + ' Starting ....')
    clear_meta_cache()


@app.on_event("shutdown")
def shutdown_event():
    log.logger.info(cfg['Application_Config'].app_name + ' Shutting Down ....')
    clear_meta_cache()

'''Admin_app'''

DEBUG = cfg['Admin_Config'].DEBUG
get_config_mode = 'Debug'
admin_app = Flask(__name__, template_folder='admin/apps/templates', static_folder='admin/apps/static')
admin_app.config.from_object(cfg['Admin_Config'])
# login
login_manager.init_app(admin_app)
# blueprint
for module_name in ('authentication', 'home'):
    module = import_module('admin.apps.{}.routes'.format(module_name))
    admin_app.register_blueprint(module.blueprint)

app.mount("/admin", WSGIMiddleware(admin_app))

'''CORS'''
origins = []

# Set all CORS enabled origins
if cfg['Application_Config'].app_cors_origins:
    origins_raw = cfg['Application_Config'].app_cors_origins.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

'''app route'''


@app.get("/",
         tags=["Default"],
         summary="Get information for this application.",
         description="Return application information",
         include_in_schema=False)
async def app_root():
    log.logger.debug('Access \'/\' : run in app_root()')
    '''
    return {
        "Application_Name": cfg['Application_Config'].app_name,
        "Version": cfg['Application_Config'].app_version,
        "Author": "ibmzhangjun@139.com",
        "Description": cfg['Application_Config'].app_description
    }
    '''
    response = RedirectResponse(url="/admin")
    return response


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(app_dir, 'admin/apps/static/favicon.ico'))

@app.get('/admin/favicon.ico', include_in_schema=False)
async def adminfavicon():
    return FileResponse(os.path.join(app_dir, 'admin/apps/static/favicon.ico'))


@app.get("/apidocs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_favicon_url="/static/favicon.ico",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/apiredoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
        with_google_fonts=False,
    )


@app.post(prefix + "/token",
          response_model=security.Token,
          tags=["Security"],
          summary="Login to get access token.",
          description="",
          )
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    log.logger.debug('Access \'/token\' : run in login_for_access_token(), '
                     'input data username: [%s] and password: [%s]' % (form_data.username, form_data.password))
    user = security.authenticate_user(users.Users().users, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=cfg['Security_Config'].access_token_expire_minutes)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(prefix + "/users",
         response_model=security.User,
         tags=["Security"],
         summary="Retrieve user information.",
         description="",
         )
async def read_users_me(current_user: security.User = Depends(security.get_current_active_user)):
    log.logger.debug('Access \'/users/me/\' : run in read_users_me()')
    return current_user


@app.get(prefix+"/_schema/database",
         tags=["Schema"],
         summary="Retrieve DbSchema Resources.",
         description="By default, all tables are returned .",
         )
async def get_schema(current_user: security.User = Depends(security.get_current_active_user)):
    log.logger.debug('Access \'/_schema\' : run in get_schema()')
    return meta.DBMeta().response_schema()


@app.get(prefix+"/_schema/_table/{table_name}",
         tags=["Schema"],
         summary="Retrieve table definition for the given table.",
         description="This describes the table, its fields and indexes.",
         )
async def get_table_schema(table_name: str, current_user: security.User = Depends(security.get_current_active_user)):
    log.logger.debug('Access \'/_schema/{table_name}\' : run in get_table_schema(), '
                     'input data table_name: [%s]' % table_name)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    return meta.DBMeta().response_table_schema(table_name)


@app.get(prefix+"/_table/{table_name}",
         tags=["Data - Table Level"],
         summary="Retrieve one or more records. ",
         description="",
         )
async def get_data(table_name: str,
                   fieldlist: str = Header('*'),
                   filter: str = Header(None),
                   filterparam: str = Header(None),
                   limit: int = Header(cfg['Query_Config'].query_default_limit, gt=0, le=cfg['Query_Config'].query_limit_upset),
                   offset: int = Header(cfg['Query_Config'].query_default_offset, gt=-1),
                   order: str = Header(None),
                   group: str = Header(None),
                   distinct: bool = Header(False),
                   count_only: bool = Header(False),
                   include_count: bool = Header(False),
                   current_user: security.User = Depends(security.get_current_active_user)):
    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **fieldlist** (header): Optional - Comma-delimited list of properties to be returned for each resource, "*" returns all properties. ex: 'id,name'
        - **filter** (header): Optional - SQL-like filter to limit the records to retrieve. ex: 'id=:qid and name=:qname'
        - **filterparam** (header): Optional - SQL-like parameter of *filter. ex: {'qid':3,'qname':'jack'}
        - **limit** (header): Optional - Set to limit the filter results.
        - **offset** (header): Optional - Set to offset the filter results to a particular record count.
        - **order** (header): Optional - SQL-like order containing field and direction for filter results. ex: 'name ASC'
        - **group** (header): Optional - Comma-delimited list of the fields used for grouping of filter results. ex: 'name'
        - **distinct** (header): Optional , default[False] - Return distinct result.
        - **count-only** (header): Optional , default[False] - Return only the total number of filter results.
        - **include-count** (header): Optional , default[False] - Include the total number of filter results in returned result.
    """

    log.logger.debug(
        'Access \'/_table/{table_name}\' : run in get_data(), input data table_name: [%s]' % table_name)
    log.logger.debug('fieldlist: [%s]' % fieldlist)
    log.logger.debug('filter: [%s]' % filter)
    log.logger.debug('filterparam: [%s]' % filterparam)
    log.logger.debug('limit: [%s]' % limit)
    log.logger.debug('offset: [%s]' % offset)
    log.logger.debug('order: [%s]' % order)
    log.logger.debug('group: [%s]' % group)
    log.logger.debug('distinct: [%s]' % distinct)
    log.logger.debug('count_only: [%s]' % count_only)
    log.logger.debug('include_count: [%s]' % include_count)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.select(fieldlist, filter, toolkit.to_dict(filterparam), limit, offset, order, group, distinct, count_only, include_count)


@app.post(prefix+"/_table/_query/{table_name}",
          tags=["Data - Table Level"],
          summary="Retrieve one or more records. ",
          description="",)
async def query_data(table_name: str, tablequerybody: apimodel.TableQueryBody,
                     current_user: security.User = Depends(security.get_current_active_user)):

    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **request body: **Required**
        ```
            {
             "fieldlist": "string",  -- Optional - Comma-delimited list of properties to be returned for each resource, "*" returns all properties. ex: 'id,name'
             "filter": "string",  -- Optional - SQL-like filter to limit the records to retrieve. ex: 'id=:qid and name=:qname'
             "filterparam": {},  -- Optional - SQL-like parameter of *filter. ex: {'qid':3,'qname':'jack'}
             "limit": 0,  -- Optional - Set to limit the filter results.
             "offset": 0,  -- Optional - Set to offset the filter results to a particular record count.
             "order": "string",  -- Optional - SQL-like order containing field and direction for filter results. ex: 'name ASC'
             "group": "string",  -- Optional - Comma-delimited list of the fields used for grouping of filter results. ex: 'name'
             "distinct": false,  -- Optional , default[False] - Return distinct result.
             "count_only": false,  -- Optional , default[False] - Return only the total number of filter results.
             "include_count": false  -- Optional , default[False] - Include the total number of filter results in returned result.
             }
        ```
    """

    log.logger.debug(
        'Access \'/_table/{table_name}/query\' : run in query_data(), input data table_name: [%s]' % table_name)
    log.logger.debug('body: [%s]' % tablequerybody)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.select(tablequerybody.fieldlist, tablequerybody.filter,
                             tablequerybody.filterparam, tablequerybody.limit, tablequerybody.offset,
                             tablequerybody.order, tablequerybody.group, tablequerybody.distinct,
                             tablequerybody.count_only, tablequerybody.include_count)


@app.post(prefix+"/_table/{table_name}",
          tags=["Data - Table Level"],
         summary="Create one or more records.",
         description="",
         )
async def post_data(table_name: str, tablepost: apimodel.TablePostBody,
                    current_user_role: bool = Depends(security.get_write_permission)):

    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **request body: Required**
        ```
            {
             "fieldvalue": "string",  -- **Required** - Dict or jason formated fieldname-fieldvalue pair. ex: '[{'name':'jack','phone':'55789'}]'
             "idfield": "string"  -- Optional - Comma-delimited list of the fields used as identifiers. ex: 'id'
             }
        ```
    """

    log.logger.debug(
        'Access \'/_table/{table_name}\' : run in post_data(), input data table_name: [%s]' % table_name)
    log.logger.debug('body: [%s]' % tablepost)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.insert(tablepost.idfield, tablepost.fieldvalue)


@app.put(prefix+"/_table/{table_name}",
         tags=["Data - Table Level"],
         summary="Update (replace) one or more records.",
         description="",
         deprecated=False
         )
async def put_data(table_name: str, tableput: apimodel.TablePutBody,
                   current_user_role: bool = Depends(security.get_write_permission)):

    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **request body: Required**
        ```
            {
             "filter": "string",  -- Optional - SQL-like filter to limit the records to retrieve. ex: 'id=:qid and name=:qname'
             "filterparam": {},  -- Optional - SQL-like parameter of *filter. ex: {'qid':3,'qname':'jack'}
             "fieldvalue": "string"  -- Optional - Dict or jason formated fieldname-fieldvalue pair. ex: '{'name':'jack','phone':'55789'}'
             }
        ```
        - **Note:** The param name in filter and filterparam **MUST NOT** equal the fieldname !
        - ex: 'id=:id' filter and  {'id':3} in filterparam will is **NOT PERMITTED** !
    """
    log.logger.debug(
        'Access \'/_table/{table_name}\' : run in put_data(), input data table_name: [%s]' % table_name)
    log.logger.debug('body: [%s]' % tableput)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.update(tableput.filter, tableput.filterparam, tableput.fieldvalue)

@app.delete(prefix+"/_table/{table_name}",
            tags=["Data - Table Level"],
            summary="Delete one or more records.",
            description="",
            )
async def delete_data(table_name: str,
                      filter: str = Header(None),
                      filterparam: str = Header(None),
                      current_user_role: bool = Depends(security.get_write_permission)):
    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **filter** (header): Optional - SQL-like filter to limit the records to retrieve. ex: 'id=:qid and name=:qname'
        - **filterparam** (header): Optional - SQL-like parameter of *filter. ex: {'qid':3,'qname':'jack'}
    """
    log.logger.debug(
        'Access \'/_table/{table_name}\' : run in delete_data(), input data table_name: [%s]' % table_name)
    log.logger.debug('filter: [%s]' % filter)
    log.logger.debug('filterparam: [%s]' % filterparam)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.delete(filter, filterparam)


@app.get(prefix+"/_table/{table_name}/{id}",
         tags=["Data - Row Level"],
         summary="Retrieve one record by identifier.",
         description="",
         )
async def get_data_by_id(table_name: str, id: str,
                         fieldlist: str = Header('*'),
                         idfield: str = Header(None),
                         current_user: security.User = Depends(security.get_current_active_user)):
    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **id** (path): **Required** - The id value of identifier
        - **fieldlist** (header): Optional - Comma-delimited list of properties to be returned for each resource, "*" returns all properties. ex: 'id,name'
        - **idfield** (header): Optional - Comma-delimited list of the fields used as identifiers. ex: 'id'
    """
    log.logger.debug(
        'Access \'/_table/{table_name}/{id}\' : run in get_data_by_id(), input data table_name: [%s]' % table_name)
    log.logger.debug('fieldlist: [%s]' % fieldlist)
    log.logger.debug('idfield: [%s]' % idfield)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.selectbyid(id, fieldlist, idfield)


@app.post(prefix+"/_table/_querybyid/{table_name}",
          tags=["Data - Row Level"],
          summary="Retrieve one record by identifier.",
          description="",
          )
async def query_data_by_id(table_name: str, tablequerybyid: apimodel.TableQueryByIdBody,
                           current_user: security.User = Depends(security.get_current_active_user)):

    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **request body: Required**
        ```
            {
            "fieldlist": "string",  -- Optional - Comma-delimited list of properties to be returned for each resource, "*" returns all properties. ex: 'id,name'
            "idfield": "string",  -- Optional - Comma-delimited list of the fields used as identifiers. ex: 'id'
            "id": "string"  -- **Required** - The id value of identifier
            }
        ```
        - **Note:** The param name in filter and filterparam **MUST NOT** equal the fieldname !
        - ex: 'id=:id' filter and  {'id':3} in filterparam will is **NOT PERMITTED** !
    """

    log.logger.debug(
        'Access \'/_table/{table_name}/querybyid\' : run in query_data_by_id(), input data table_name: [%s]' % table_name)
    log.logger.debug('body: [%s]' % tablequerybyid)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.selectbyid(tablequerybyid.id, tablequerybyid.fieldlist, tablequerybyid.idfield)


@app.put(prefix+"/_table/{table_name}/{id}",
         tags=["Data - Row Level"],
         summary="Replace the content of one record by identifier.",
         description="",
         )
async def put_data_by_id(table_name: str, id: str,
                         tableputbyid: apimodel.TablePutByIdBody,
                         current_user_role: bool = Depends(security.get_write_permission)):

    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **id** (path): **Required** - The id value of identifier
        - **request body: Required**
        ```
            {
            "fieldvalue": "string"  -- Optional - Dict or jason formated fieldname-fieldvalue pair. ex: '[{'name':'jack','phone':'55789'}]'
            "idfield": "string",  -- Optional - Comma-delimited list of the fields used as identifiers. ex: 'id'
            }
        ```
        - **Note:** The param name in filter and filterparam **MUST NOT** equal the fieldname !
        - ex: 'id=:id' filter and  {'id':3} in filterparam will is **NOT PERMITTED** !
    """
    log.logger.debug(
        'Access \'/_table/{table_name}/{id}\' : run in put_data_by_id(), input data table_name: [%s]' % table_name)
    log.logger.debug('body: [%s]' % tableputbyid)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.updatebyid(tableputbyid.idfield, id, tableputbyid.fieldvalue)


@app.delete(prefix+"/_table/{table_name}/{id}",
            tags=["Data - Row Level"],
            summary="Delete one record by identifier.",
            description="",
            )
async def delete_data_by_id(table_name: str, id: str,
                            idfield: str = Header(None, max_length=200),
                            current_user_role: bool = Depends(security.get_write_permission)):

    """
        Parameters
        - **table_name** (path): **Required** - Name of the table to perform operations on.
        - **id** (path): **Required** - The id value of identifier
        - **idfield** (header): Optional - Comma-delimited list of the fields used as identifiers. ex: 'id'
    """
    log.logger.debug(
        'Access \'/_table/{table_name}/{id}\' : run in delete_data_by_id(), input data table_name: [%s]' % table_name)
    log.logger.debug('id: [%s]' % id)
    log.logger.debug('idfield: [%s]' % idfield)
    if not meta.DBMeta().check_table_schema(table_name):
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='Table [ %s ] not found' % table_name
        )
    ptable = tablemodel.TableModel(table_name)
    return ptable.deletebyid(idfield, id)


if cfg['Application_Config'].app_user_func:
    log.logger.info('Add Custom query ...')
    qdef = querydef.QueryDef()
    desstr = "**USAGE:**<br/><br/>"
    for ufunc in qdef.custom_dict.values():
        desstr = desstr + "**{func_name}="+ufunc['func_name']+"**    "+ufunc['description']+"<br/>"
    @app.get(prefix+"/_userfunc/{func_name}",
             tags=["USER"],
             summary="Usser Defined functions.",
             description=desstr,
             )
    async def userquery(func_name: str, sqlparam: str = Header(None),
                               current_user: security.User = Depends(security.get_current_active_user)):
        log.logger.debug('Access \'/_userfunc/%s\' : run in userquery()' % func_name)
        log.logger.debug('sqlparam: [%s]' % sqlparam)
        uf = userfunc.UserFunc(func_name)
        if qdef.getsql(func_name) is not None:
            return uf.query(qdef.getsql(func_name), sqlparam)
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail='UserFunction [ %s ] not found' % func_name
            )

    @app.post(prefix+"/_userfunc/{func_name}",
             tags=["USER"],
             summary="Usser Defined functions.",
             description=desstr,
             )
    async def userquerypost(func_name: str, ufbody: apimodel.UserFuncPostBody,
                               current_user: security.User = Depends(security.get_current_active_user)):
        log.logger.debug('Access \'/_userfunc/%s\' : run in userquery()' % func_name)
        log.logger.debug('body: [%s]' % ufbody)
        uf = userfunc.UserFunc(func_name)
        if qdef.getsql(func_name) is not None:
            return uf.query(qdef.getsql(func_name),ufbody.sqlparam)
        else:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail='UserFunction [ %s ] not found' % func_name
            )


@app.get("/sys/config",
         tags=["System"],
         summary="Show the system configuration.",
         description="",
         )
async def sys_config(SecuretKey: str = Header(..., min_length=5),
                      current_user_role: bool = Depends(security.get_super_permission)):
    """
        Please use 'app_confirm_key' as SecuretKey to confirm the operation
        - **SecuretKey** (header): **Required** - use 'app_confirm_key' default value is 'Confirmed'.
    """
    log.logger.debug(
        'Access \'/sys/config\' : run in main.py, input data: [ %s ]' % SecuretKey)
    if SecuretKey == cfg['Application_Config'].app_confirm_key:
        return {
            "System_Config": cfg
        }
    else:
        return {
            "System_Config": 'Operation Aborted'
        }


@app.get("/sys/reloadmeta",
         tags=["System"],
         summary="Reload the Database Schema .",
         description="",
         )
async def reload_meta(SecuretKey: str = Header(..., min_length=5),
                      current_user_role: bool = Depends(security.get_super_permission)):

    """
        Please use 'app_confirm_key' as SecuretKey to confirm the operation
        - **SecuretKey** (header): **Required** - use 'app_confirm_key' default value is 'Confirmed'.
    """
    log.logger.debug(
        'Access \'/sys/reloadmeta\' : run in reload_meta(), input data: [ %s ]' % SecuretKey)
    if SecuretKey == cfg['Application_Config'].app_confirm_key:
        clear_meta_cache()
        schema_file = meta.DBMeta().schema_file()
        if os.path.exists(schema_file):
            os.remove(schema_file)
        meta.DBMeta().load_metadata()
        meta.DBMeta().gen_schema()
        meta.DBMeta().load_schema()
        return {
            "Reload_Meta": 'Sucessful'
        }
    else:
        return {
            "Reload_Meta": 'Operation Aborted'
        }


@app.get("/sys/status",
         tags=["System"],
         summary="Show the database connection pool status.",
         description="",
         )
async def sys_status(SecuretKey: str = Header(..., min_length=5),
                      current_user_role: bool = Depends(security.get_super_permission)):
    """
        Please use 'app_confirm_key' as SecuretKey to confirm the operation
        - **SecuretKey** (header): **Required** - use 'app_confirm_key' default value is 'Confirmed'.
    """
    log.logger.debug(
        'Access \'/sys/status\' : run in main.py, input data: [ %s ]' % SecuretKey)
    if SecuretKey == cfg['Application_Config'].app_confirm_key:
        return {
            "Pool_status": dbengine.DBEngine().connect().pool.status()
        }
    else:
        return {
            "Sys_status": 'Operation Aborted'
        }


def clear_meta_cache():
    # cache file define
    metadata_pickle_filename = cfg['Schema_Config'].schema_cache_filename
    cache_path = os.path.join(os.path.expanduser("~"), ".neptune_cache")
    cache_file = os.path.join(cache_path, metadata_pickle_filename)
    if os.path.exists(cache_file):
        os.remove(cache_file)
        log.logger.info('API cache cleared ....')
    else:
        log.logger.info('API cache does not exists ....')
