#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import traceback

from simple_rest_client.api import API
from simple_rest_client.resource import AsyncResource
from config import config
from datetime import datetime, timedelta
from util import log
import simplejson as json

'''config'''
cfg = config.Config()

'''logging'''
log = log.Logger(level=cfg.application['app_log_level'])

class NeptuneClient():
    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._lastlogin = 0
        self._token_expired = True
        self._access_token = None
        self._token_type = 'bearer'
        self._api_root_url = 'http://127.0.0.1:' + str(cfg.application['app_http_port']) + cfg.application['app_prefix'] + '/'
        self._api_client = API(api_root_url = self._api_root_url, params = {}, headers = {}, timeout = 3, append_slash = False, json_encode_body = False, ssl_verify=False)


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
            self._token_expired = datetime.utcnow() - self._lastlogin > timedelta(minutes=cfg.security['access_token_expire_minutes'] - 1)
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

    def fetchme(self):
        api = self._api_client
        api.headers = {'Authorization': 'Bearer ' + self.access_token}
        api.api_root_url = self.api_root_url + 'users/'
        api.add_resource(resource_name='me')
        try:
            response = api.me.list()
            return response.body
        except Exception as exp:
            log.logger.error('Exception at fetch() %s ' % exp)
            traceback.print_exc()

    def fetch(self, resource_name, url_prefix='', action='list', body=None):
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
                # log.logger.debug(res.actions)
                # log.logger.debug(res.get_action_full_url(action))
                # log.logger.debug(res.get_action(action))
                func = getattr(res,action)
                response = None
                if body is not None:
                    response = func(body)
                else:
                    response = func()
                log.logger.debug(response.body)
                return response.body
            except Exception as exp:
                log.logger.error('Exception at fetch() %s ' % exp)
                traceback.print_exc()

if __name__ == '__main__':
    nc = NeptuneClient('admin','admin')
    if nc.token_expired:
        nc.renew_token()
    if ( not nc.token_expired ) and ( nc.access_token is not None ):
        log.logger.debug(nc.fetchme())
        nc.fetch('database','_schema')
        nc.fetch('orders','_schema/_table')

