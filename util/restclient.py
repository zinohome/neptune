#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import traceback

from simple_rest_client.api import API
from config import config
from datetime import datetime, timedelta
from util import log
import json
from pandas import json_normalize

'''config'''
cfg = config.app_config

'''logging'''
log = log.Logger(level=cfg['Application_Config'].app_log_level)

class NeptuneClient():
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._lastlogin = 0
        self._token_expired = True
        self._access_token = None
        self._token_type = 'bearer'
        httpstr = 'https' if cfg['Application_Config'].app_admin_use_https else 'http'
        self._api_root_url = httpstr + '://127.0.0.1:' + str(cfg['Application_Config'].app_http_port) + cfg['Application_Config'].app_prefix + '/'
        self._api_client = API(api_root_url = self._api_root_url, params = {}, headers = {}, timeout = cfg['Application_Config'].app_http_timeout, append_slash = False, json_encode_body = False, ssl_verify=False)


    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def lastlogin(self):
        return self._lastlogin

    @property
    def token_expired(self):
        if self._lastlogin == 0:
            self._token_expired = True
        else:
            self._token_expired = datetime.utcnow() - self._lastlogin > timedelta(minutes=cfg['Security_Config'].access_token_expire_minutes - 1)
        return self._token_expired

    @property
    def access_token(self):
        return self._access_token

    @property
    def token_type(self):
        return self._token_type

    @property
    def api_root_url(self):
        return self._api_root_url

    def renew_token(self):
        api = self._api_client
        api.add_resource(resource_name='token')
        request_body = {"username": self.username,"password": self.password}
        try:
            response = api.token.create(body = request_body)
            if response.status_code == 200:
                self._access_token = response.body['access_token']
                self._token_type = response.body['token_type']
                self._lastlogin = datetime.utcnow()
            else:
                log.logger.error('Can not get renew_token at renew_token() ... ')
                raise Exception('Can not get renew_token at renew_token()')
        except Exception as exp:
            log.logger.error('Exception at renew_token() %s ' % exp)
            traceback.print_exc()

    def user_login(self):
        login_pass = False
        api = self._api_client
        api.add_resource(resource_name='token')
        request_body = {"username": self.username,"password": self.password}
        try:
            response = api.token.create(body = request_body)
            if response.status_code == 200:
                self._access_token = response.body['access_token']
                self._token_type = response.body['token_type']
                self._lastlogin = datetime.utcnow()
                login_pass = True
            else:
                log.logger.error('Can not get user login at user_login() ... ')
        except Exception as exp:
            log.logger.error('Exception at user_login() %s ' % exp)
        return login_pass

    def fetchusers(self):
        api = self._api_client
        api.headers = {'Authorization': 'Bearer ' + self.access_token}
        api.api_root_url = self.api_root_url
        api.add_resource(resource_name='users')
        try:
            response = api.users.list()
            return response.body
        except Exception as exp:
            log.logger.error('Exception at fetchusers() %s ' % exp)
            traceback.print_exc()

    def fetch(self, resource_name, url_prefix='', body=None, offset=None, limit=None, withcounters=None):
        action = 'list'
        if self.token_expired:
            self.renew_token()
        if (not self.token_expired) and (self.access_token is not None):
            # log.logger.debug('access_token : %s' % self.access_token)
            api = self._api_client
            api.headers = {'Authorization': 'Bearer ' + self.access_token}
            if offset is not None:
                api.headers['offset'] = str(offset)
            if limit is not None:
                api.headers['limit'] = str(limit)
            if withcounters is not None:
                api.headers['include-count'] = str(withcounters)
            api.api_root_url = self.api_root_url + url_prefix
            api.add_resource(resource_name=resource_name)
            try:
                res = api._resources[api.correct_attribute_name(resource_name)]
                # log.logger.debug(res.actions)
                # log.logger.debug(res.get_action_full_url(action))
                # log.logger.debug(res.get_action(action))
                func = getattr(res,action)
                response = None
                if body is not None:
                    response = func(body)
                else:
                    response = func()
                res = {'code': response.status_code, 'body': response.body}
                return res
            except Exception as exp:
                log.logger.error('Exception at fetch() %s ' % exp)
                traceback.print_exc()

    def post(self, resource_name, url_prefix='', body=None):
        log.logger.debug(body)
        action = 'create'
        if self.token_expired:
            self.renew_token()
        if (not self.token_expired) and (self.access_token is not None):
            # log.logger.debug('access_token : %s' % self.access_token)
            api = self._api_client
            api.headers = {'Authorization': 'Bearer ' + self.access_token}
            api.api_root_url = self.api_root_url + url_prefix
            api.add_resource(resource_name=resource_name)
            try:
                res = api._resources[api.correct_attribute_name(resource_name)]
                func = getattr(res,action)
                response = None
                if body is not None:
                    response = func(body=body)
                    res = {'code': response.status_code, 'body': response.body}
                else:
                    res = {'code': response.status_code, 'body': response.body}
                return res
            except Exception as exp:
                log.logger.error('Exception at post() %s ' % exp)
                traceback.print_exc()


    def put(self, resource_name, url_prefix='', body=None, idfield=None, idvalue=None):
        log.logger.debug(body)
        action = 'update'
        if self.token_expired:
            self.renew_token()
        if (not self.token_expired) and (self.access_token is not None):
            # log.logger.debug('access_token : %s' % self.access_token)
            api = self._api_client
            api.headers = {'Authorization': 'Bearer ' + self.access_token}
            if idfield is not None:
                api.headers['idfield'] = str(idfield)
            api.api_root_url = self.api_root_url + url_prefix
            api.add_resource(resource_name=resource_name, full_action_url=api.api_root_url + '/' + resource_name + '/' + idvalue)
            try:
                res = api._resources[api.correct_attribute_name(resource_name)]
                func = getattr(res,action)
                response = None
                if body is not None:
                    response = func(body=body)
                    res = {'code': response.status_code, 'body': response.body}
                else:
                    res = {'code': response.status_code, 'body': response.body}
                return res
            except Exception as exp:
                log.logger.error('Exception at post() %s ' % exp)
                traceback.print_exc()


    def deletebyid(self, resource_name, url_prefix='', idfield=None, idvalue=None):
        action = 'destroy'
        if self.token_expired:
            self.renew_token()
        if (not self.token_expired) and (self.access_token is not None):
            # log.logger.debug('access_token : %s' % self.access_token)
            api = self._api_client
            api.headers = {'Authorization': 'Bearer ' + self.access_token}
            if idfield is not None:
                api.headers['idfield'] = str(idfield)
            api.api_root_url = self.api_root_url + url_prefix
            api.add_resource(resource_name=resource_name, full_action_url=api.api_root_url + '/' + resource_name + '/' + idvalue)
            try:
                res = api._resources[api.correct_attribute_name(resource_name)]
                # log.logger.debug(res.actions)
                # log.logger.debug(res.get_action_full_url(action))
                # log.logger.debug(res.get_action(action))
                func = getattr(res,action)
                response = None
                response = func()
                res = {'code':response.status_code, 'body':response.body}
                return res
            except Exception as exp:
                log.logger.error('Exception at deletebyid() %s ' % exp)
                traceback.print_exc()

    def toDataFrame(self, jsonobj, attbname):
        dataframe = json_normalize(jsonobj[attbname])
        return dataframe


if __name__ == '__main__':
    nc = NeptuneClient('admin','admin')
    log.logger.debug(nc.user_login())
    if nc.token_expired:
        nc.renew_token()
    if ( not nc.token_expired ) and ( nc.access_token is not None ):
        log.logger.debug(nc.fetchusers())
        # nc.fetch('database','_schema')
        ncmeta = nc.fetch('Brands', '_schema/_table')
        log.logger.debug(ncmeta)
        #resultstr = nc.fetch('orders','_schema/_table')
        #log.logger.debug(resultstr)
        #resultstr = nc.fetch('orders', '_table', None, 10, 10, True)
        #log.logger.debug(resultstr)
        #resultstr = nc.deletebyid('employees', '_table', 'employeeNumber', '1002')
        #log.logger.debug(resultstr)
        #resultstr = nc.post('zinopara', '_table', json.dumps({"fieldvalue":"{'id': '229', 'type': '222', 'creatorid': '222', 'json': '222', 'json_updates': '2222'}"}))
        #log.logger.debug(resultstr)

        # log.logger.debug(dir(resultstr))
        # df = nc.toDataFrame(resultstr,'data')
        # log.logger.debug(df.to_html(table_id="example", classes="table table-bordered table-striped"))

