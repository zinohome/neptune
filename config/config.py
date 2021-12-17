#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  #
#  Copyright (C) 2021 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2021
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: Neptune

from unipath import Path
from decouple import config


class Config(object):
    BASE_DIR = Path(__file__).parent
    config.encoding = 'utf-8'
    config.search_path = BASE_DIR

class Application_Config(Config):
    app_name = config('app_name', default = 'Neptune')
    app_version = config('app_version', default = 'v1.1.2')
    app_description = config('app_description', default = 'Zero Code REST API for RDBMS')
    app_prefix = config('app_prefix', default = '/api/v1')
    app_cors_origins = config('app_cors_origins', default = '*')
    app_param_prefix = config('app_param_prefix', default = 'up_b_')
    app_force_generate_meta = config('app_force_generate_meta', default = True, cast = bool)
    app_log_level = config('app_log_level', default = 'INFO')
    app_user_func = config('app_user_func', default = True, cast = bool)
    app_exception_detail = config('app_exception_detail', default = True, cast = bool)
    app_admin_use_https = config('app_admin_use_https', default = True, cast = bool)
    app_confirm_key = config('app_confirm_key', default = 'Confirmed')
    app_http_port = config('app_http_port', default = 8890, cast = int)
    app_http_timeout = config('app_http_timeout', default = 3, cast = int)
    app_load_metadat_on_load = config('app_load_metadat_on_load', default = True, cast = bool)
    app_clear_metadat_on_startup = config('app_clear_metadat_on_startup', default = True, cast = bool)
    app_clear_metadat_on_shutdown = config('app_clear_metadat_on_shutdown', default = True, cast = bool)

class Schema_Config(Config):
    schema_cache_enabled = config('schema_cache_enabled', default = True, cast = bool)
    schema_cache_filename = config('schema_cache_filename', default = 'neptune_metadata')
    schema_db_metafile = config('schema_db_metafile', default = 'metadata.json')
    schema_fetch_all_table = config('schema_fetch_all_table', default = True, cast = bool)
    schema_fetch_tables = config('schema_fetch_tables', default = '[test,faultmsg]')

class Query_Config(Config):
    query_limit_upset = config('query_limit_upset', default = 2000, cast = int)
    query_default_limit = config('query_default_limit', default = 20, cast = int)
    query_default_offset = config('query_default_offset', default = 0, cast = int)

class Security_Config(Config):
    security_key = config('security_key', default = '47051d5e3bafcfcba3c80d6d1119a7adf78d2967a8972b00af1ea231ca61f589')
    security_algorithm = config('security_algorithm', default = 'HS256')
    access_token_expire_minutes = config('access_token_expire_minutes', default = 30, cast = int)

class Database_Config(Config):
    db_gendburi = config('db_gendburi', default = True, cast = bool)
    db_dialect = config('db_dialect', default = 'mysql')
    db_drivername = config('db_drivername', default = 'mysql+pymysql')
    db_host = config('db_host', default = '192.168.50.10')
    db_port = config('db_port', default = 3306, cast = int)
    db_name = config('db_name', default = 'mysqlsrc')
    db_schema = config('db_schema', default = 'mysqlsrc')
    db_use_schema = config('db_use_schema', default = True, cast = bool)
    db_username = config('db_username', default = 'root')
    db_password = config('db_password', default = 'passw0rd')
    db_uri = config('db_uri', default = 'mysql+pymysql://root:passw0rd@192.168.50.10:3306/mysqlsrc')
    db_exclude_tablespaces = config('db_exclude_tablespaces', default = '[SYSTEM,SYSAUX]')

class Connection_Config(Config):
    con_pool_size = config('con_pool_size', default = 20, cast = int)
    con_max_overflow = config('con_max_overflow', default = 5, cast = int)
    con_pool_use_lifo = config('con_pool_use_lifo', default = True, cast = bool)
    con_pool_pre_ping = config('con_pool_pre_ping', default = True, cast = bool)
    con_pool_recycle = config('con_pool_recycle', default = 3600, cast = int)

class Admin_Config(Config):
    DEBUG = config('DEBUG', default = False, cast = bool)
    SECRET_KEY = config('SECRET_KEY', default = 'bgt56yhn@Passw0rd')
    SESSION_COOKIE_HTTPONLY = config('SESSION_COOKIE_HTTPONLY', default = True, cast = bool)
    REMEMBER_COOKIE_HTTPONLY = config('REMEMBER_COOKIE_HTTPONLY', default = True, cast = bool)
    REMEMBER_COOKIE_DURATION = config('REMEMBER_COOKIE_DURATION', default = 3600, cast = int)

# Load all possible configurations
app_config = {
    'Application_Config': Application_Config,
    'Schema_Config': Schema_Config,
    'Query_Config': Query_Config,
    'Security_Config': Security_Config,
    'Database_Config': Database_Config,
    'Connection_Config': Connection_Config,
    'Admin_Config': Admin_Config
}
def recofig():
    Application_Config = None
    Schema_Config = None
    Query_Config = None
    Security_Config = None
    Database_Config = None
    Connection_Config = None
    Admin_Config = None
    app_config = {}
    app_config['Application_Config'] = Application_Config
    app_config['Schema_Config'] = Schema_Config
    app_config['Query_Config'] = Query_Config
    app_config['Security_Config'] = Security_Config
    app_config['Database_Config'] = Database_Config
    app_config['Connection_Config'] = Connection_Config
    app_config['Admin_Config'] = Admin_Config




if __name__ == '__main__':
    #print(dir(app_config['Application_Config']))
    #print(app_config['Application_Config'].__dict__)
    #print(app_config['Application_Config'].app_description)
    #print(app_config['Schema_Config'].schema_fetch_tables)
    #print(app_config['Database_Config'].db_uri)
    #print(app_config['Database_Config'].db_exclude_tablespaces)
    #print(app_config['Schema_Config'].schema_fetch_tables)
    recofig()
    print(app_config['Application_Config'].__dict__)
    print(app_config['Schema_Config'].__dict__)
    print(app_config['Query_Config'].__dict__)
    print(app_config['Security_Config'].__dict__)
    print(app_config['Database_Config'].__dict__)
    print(app_config['Connection_Config'].__dict__)
    print(app_config['Admin_Config'].__dict__)